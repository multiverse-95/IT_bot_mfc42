from aiogram import Dispatcher, types
# Импорт регулярных выражений
import re
# Импорт библиотек для бота
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# Импорт конфигурационного файла
from fsm.app.config_reader import load_config
from aiogram.types import ParseMode
# Получение данных с конфигурационного файла
config = load_config("config/bot.ini")
# Получение id админ группы
admin_group_id = int(config.tg_bot.admin_group_id)

# Данные по 1с
# Регулярные выражения для 1с
regexp_1c = '(\W|^).*1с.*завис.*(\W|$)|(\W|^).*завис.*1с(\W|$)|(\W|^).*не\sработ.*1с(\W|$)|(\W|^).*1с.*не\sработ.*(\W|$)' \
            '|(\W|^).*1с.*весит(\W|$)|(\W|^).*1с.*висит.*(\W|$)|(\W|^).*весит.*1с(\W|$)|(\W|^).*висит.*1с(\W|$)|(\W|^).*1с.*почин.*(\W|$)|(\W|^).*почин.*1с(\W|$)'
# Список проблем с 1с
available_buh_1C_problems = ["Не работает/завис 1С", "Другая проблема с 1С"]
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
# Класс для 1с
class OrderBuh1C(StatesGroup):
    waiting_for_buh_1C_problem = State()
    waiting_for_other_buh_1C_problem = State()

# Начало работы с 1с
async def buh_1C_start(message: types.Message):
    # Создание кнопок с проблемами по 1с
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_buh_1C_problems)
    # for name in available_buh_1C_problems:
    #     keyboard.add(name)
    # Бот спрашивает про проблему с 1с
    await message.answer("📚 Какая у вас проблема с 1С? ", reply_markup=keyboard)
    # Бот ожидает следующее состояние с проблемой 1с
    await OrderBuh1C.waiting_for_buh_1C_problem.set()

# Выбор проблемы с 1с
async def buh_1C_problem_chosen(message: types.Message, state: FSMContext):
    # Если выбран вариант с кнопки или совпало с регулярными выражениями
    if message.text in available_buh_1C_problems or re.match(regexp_1c, message.text.lower()):
        # Если выбрана другая проблема с 1с
        if message.text == available_buh_1C_problems[len(available_buh_1C_problems) - 1]:
            # Записать во временное хранилище информацию
            await state.update_data(chosen_buh_1C_problem=message.text.lower())
            # Бот предлагает описать проблему с 1с
            await message.answer("⚠ Пожалуйста, напишите вашу проблему с 1С. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующее состояние с выбором проблемы
            await OrderBuh1C.waiting_for_other_buh_1C_problem.set()
        # Иначе если выбран вариант с зависанием 1с
        else:
            # Записываем во временное хранилище информацию
            await state.update_data(chosen_buh_1C_server_problem=message.text.lower())
            # Бот сообщает, что сервер 1с будет перезагружен
            await message.answer("⚠ Сервер 1С будет перезагружен. Пожалуйста, подождите 5 минут...",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот считывает информацию со временного хранилища
            user_data = await state.get_data()
            # Сообщение в группу
            answer_to_group = f"📚 ⚠ Проблема с 1С: {user_data['chosen_buh_1C_server_problem'].lower()}"
            # Бот предлагает выбрать другие функции
            await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
            # Бот отправляет сообщение в группу
            await message.bot.send_message(admin_group_id, answer_to_group)
            # Бот пересылает сообщение от пользователя
            await message.forward(admin_group_id)
            # Бот завершает состояние
            await state.finish()
    # Если выбран вариант не с кнопки, или не совпало с регулярными выражениями
    elif message.text not in available_buh_1C_problems:
        # Бот сообщает выбрать вариант с клавиатуры
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        # Создание кнопок с проблемами 1с
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_buh_1C_problems)
        # Бот спрашивает про проблему с 1с
        await message.answer("📚 Какая у вас проблема с 1С? ", reply_markup=keyboard)
        return

# Функция для других проблем с 1с
async def buh_1C_other_problem_chosen(message: types.Message, state: FSMContext):
    # Если пользователь отправил документ
    if message.content_type == 'document':
        # Ответ в группу
        answer_to_group = f"📚 ⚠ Проблема с 1С..."
        # Бот сообщает, что выслал информацию в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот присылает сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение от пользователя
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    # Если пользователь отправил фотографию
    elif message.content_type == 'photo':
        # Сообщение в группу
        answer_to_group = f"📚 ⚠ Проблема с 1С..."
        # Бот сообщает, что выслал информацию в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот присылает сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение от пользователя
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
    # Если пользователь отправил текстовую информацию
    elif message.content_type == 'text':
        # Запись данных во временное хранилище
        await state.update_data(chosen_buh_1C_problem=message.text.lower())
        # Получение данных с временного хранилища
        user_data = await state.get_data()
        # Текст ответа
        answer_to_message = f"⚠ У вас текущая проблема с 1С: {user_data['chosen_buh_1C_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        # Ответ в группу
        answer_to_group = f"📚 ⚠ Проблема с 1С: {user_data['chosen_buh_1C_problem'].lower()}"
        # Бот отвечает на сообщение пользователя
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот присылает сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение от пользователя
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()

# Хэндлеры для проблем с 1с
def register_handlers_buh_1C(dp: Dispatcher):
    # Хэндлер для команды с 1с
    dp.register_message_handler(buh_1C_start, commands="1c", state="*")
    # Хэндлер для выбора проблем с 1с
    dp.register_message_handler(buh_1C_problem_chosen, state=OrderBuh1C.waiting_for_buh_1C_problem)
    # Хэндлер для выбора других проблем с 1с
    dp.register_message_handler(buh_1C_other_problem_chosen, content_types=types.ContentType.all(), state=OrderBuh1C.waiting_for_other_buh_1C_problem)
    # Поиск через регулярные выражения с выбором проблем с 1с
    dp.register_message_handler(buh_1C_problem_chosen, regexp=regexp_1c, state="*")
    # Регулярные выражения для определения вопроса с 1с
    dp.register_message_handler(buh_1C_start, regexp="(\W|^)1c.*(\W|$)|(\W|^)1с.*(\W|$)|(\W|^)один\s.с.*(\W|$)|(\W|^)1\s.с.*(\W|$)", state="*")

