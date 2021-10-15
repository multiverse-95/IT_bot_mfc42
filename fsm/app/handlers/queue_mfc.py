# Импорт библиотек для бота
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
# Импорт конфигурационного файла
from fsm.app.config_reader import load_config
# Получение данных с конфигурационного файла
config = load_config("config/bot.ini")
# Получение id админ группы
admin_group_id = int(config.tg_bot.admin_group_id)
# Регулярные выражения для очереди
regexp_queue = '(\W|^)очередь.*(\W|$)|(\W|^)проблема.*очеред.*(\W|$)|(\W|^)не\sработ.*очеред.*(\W|$)'
# Список проблем по очереди
available_queue_problems = ["Завис талон", "Завис терминал", "Завис монитор", "Зависли кнопки", "Другая проблема с очередью"]
# Другие функции
other_functions = "<i>Попробуйте другие функции:</i> \n" \
                  "<b>АИС, ПК ПВД, 1C, Очередь</b> \n" \
                  "/ais - 🖥️ вопросы по АИС \n" \
                  "/pkpvd - 📋 вопросы по ПК ПВД \n" \
                  "/1c - 📚 вопросы по 1C \n" \
                  "/queue - ⏳ вопросы по очереди \n" \
                  "<b>Техника и другое</b> \n" \
                  "/printer - 🖨️ вопросы по принтеру \n" \
                  "/cancel - 🚫 отменить текущее действие "
# Класс для очереди
class OrderQueue(StatesGroup):
    waiting_for_queue_problem = State()
    waiting_for_queue_talon_problem = State()
    waiting_for_other_queue_problem = State()

# Начало работы с очередью
async def queue_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for name in available_queue_problems:
    #     keyboard.add(name)
    # Расположим кнопки в ряд
    keyboard.row(available_queue_problems[0], available_queue_problems[1])
    keyboard.row(available_queue_problems[2], available_queue_problems[3])
    keyboard.row(available_queue_problems[4])
    # Бот спрашивает про проблему с очередью
    await message.answer("⏳ Какая у вас проблема с очередью? ", reply_markup=keyboard)
    # Бот ожидает следующего состояния с выбором проблемы с очередью
    await OrderQueue.waiting_for_queue_problem.set()

# Функция выбора проблемы с очередью
async def queue_problem_chosen(message: types.Message, state: FSMContext):
    # Если текст выбран не из кнопок
    if message.text not in available_queue_problems:
        # Бот предложит выбрать текст из кнопок
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Расположим кнопки в ряд
        keyboard.row(available_queue_problems[0], available_queue_problems[1])
        keyboard.row(available_queue_problems[2], available_queue_problems[3])
        keyboard.row(available_queue_problems[4])
        # Бот спросит про вашу проблему с очередью
        await message.answer("⏳ Какая у вас проблема с очередью? ", reply_markup=keyboard)
        return
    # Если выбран вариант с кнопок
    if message.text in available_queue_problems:
        # Если выбрана другая проблема с очередью
        if message.text == available_queue_problems[len(available_queue_problems) - 1]:
            # Запись во временное хранилище
            await state.update_data(chosen_queue_problem=message.text.lower())
            # Бот предлагает сообщить про проблему с очередью
            await message.answer("⚠ Пожалуйста, напишите вашу проблему с очередью. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующего состояния
            await OrderQueue.waiting_for_other_queue_problem.set()
        # Иначе, если выбрана проблема с зависшим талоном
        elif message.text == available_queue_problems[0]:
            # Запись во временное хранилище данных
            await state.update_data(chosen_queue_problem=message.text.lower())
            # Бот предлагает прикрепить зависший талон
            await message.answer("⚠ Пожалуйста, прикрепите скриншот с зависшим талоном...",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующего действия
            await OrderQueue.waiting_for_queue_talon_problem.set()
        # Если выбраны остальные проблемы
        else:
            # Запись во временное хранилище
            await state.update_data(chosen_queue_problem=message.text.lower())
            # Бот сообщае, что информация выслана в it-отдел
            await message.answer("⚠ Информация была выслана в IT-отдел",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Чтение данных из временного хранилища
            user_data = await state.get_data()
            # Сообщение в группу
            answer_to_group = f"⏳ ⚠ Проблема с очередью: {user_data['chosen_queue_problem'].lower()}"
            # Бот предлагает выбрать другие функции
            await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
            # Бот отправляет сообщение в группу
            await message.bot.send_message(admin_group_id, answer_to_group)
            # Бот пересылает сообщение от пользователя
            await message.forward(admin_group_id)
            # Бот завершает состояние
            await state.finish()

# Функция для обработки других проблем с очередью
async def queue_other_problem_chosen(message: types.Message, state: FSMContext):
    # Если пользователь выбрал документ
    if message.content_type == 'document':
        # Ответ в группу
        answer_to_group = f"⏳ ⚠ Проблема с очередью..."
        # Бот сообщает информацию в группу
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    # Если пользователь выбрал фотографию
    elif message.content_type == 'photo':
        # Ответ в группу
        answer_to_group = f"⏳ ⚠ Проблема с очередью..."
        # Бот сообщает информацию в группу
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
    # Если пользователь написал текстовую информацию
    elif message.content_type == 'text':
        print("test text")
        # Запись данных во временное хранилище
        await state.update_data(chosen_queue_problem=message.text.lower())
        # Получение данных с временного хранилища
        user_data = await state.get_data()
        # Сообщение пользователю
        answer_to_message = f"⚠ У вас текущая проблема с очередью: {user_data['chosen_queue_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        # Сообщению в группу
        answer_to_group = f"⏳ ⚠ Проблема с очередью: {user_data['chosen_queue_problem'].lower()}"
        # Бот отвечает пользователю
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()

# Функция для выбора проблемы с талоном
async def queue_talon_problem(message: types.Message, state: FSMContext):
    # Если пользователь выбрал документ
    if message.content_type == 'document':
        # Сообщению в группу
        answer_to_group = f"⏳ ⚠ Проблема с талоном в очереди... Надо что-то делать..."
        # Бот сообщает в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    # Если пользователь выбрал фотографию
    elif message.content_type == 'photo':
        # Сообщение в группу
        answer_to_group = f"⏳ ⚠ Проблема с талоном в очереди... Надо что-то делать..."
        # Бот сообщает в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
    # Если пользователь написал текст
    elif message.content_type == 'text':
        print("test text")
        # Запись во временное хранилище
        await state.update_data(chosen_queue_problem=message.text.lower())
        # Считывание со временного хранилища
        user_data = await state.get_data()
        # Ответ на сообщение
        answer_to_message = f"⚠ У вас текущая проблема с очередью: {user_data['chosen_queue_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        # Ответ в группу
        answer_to_group = f"⏳ ⚠ Проблема с талоном в очереди... Надо что-то делать... {user_data['chosen_queue_problem'].lower()}"
        # Бот отвечает на сообщение
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()

# Регистрация хэндлеров для очереди
def register_handlers_queue(dp: Dispatcher):
    # Хэндлер для команды очереди
    dp.register_message_handler(queue_start, commands="queue", state="*")
    # Хэндлер для выбора проблемы с очередью
    dp.register_message_handler(queue_problem_chosen, state=OrderQueue.waiting_for_queue_problem)
    # Хэндлер для выбора проблемы с талоном
    dp.register_message_handler(queue_talon_problem, content_types=types.ContentType.all(), state=OrderQueue.waiting_for_queue_talon_problem)
    # Хэндлер для другой проблемы
    dp.register_message_handler(queue_other_problem_chosen, content_types=types.ContentType.all(), state=OrderQueue.waiting_for_other_queue_problem)
    # Поиск через регулярные выражения
    dp.register_message_handler(queue_start, regexp=regexp_queue, state="*")

