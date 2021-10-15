# Импорт регулярных выражений
import re
# Импорт библиотек для бота
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.dispatcher.webhook import SendMessage
from aiogram.types import ParseMode

# Импорт конфигурационного файла
from fsm.app.config_reader import load_config
# Получение данных с конфигурационного файла
config = load_config("config/bot.ini")
# Получение id админ группы
admin_group_id = int(config.tg_bot.admin_group_id)

# Данные о принтерах
# Регулярные выражения для определения проблемы с принтером
regexp_printer = '.*картридж.*|.*тонер.*|.*чернил.*|.*не.*работ.*|.*не.*печат.*|.*ломалс.*'
# Список проблем с принтерами
available_printer_problems = ["картридж закончился", "плохо печатает", "не печатает", "другая проблема"]
# Список моделей принтеров
available_printer_names = ["1025", "2540", "2235", "2035", "2530", "1030", "другая модель", "не могу определить модель"]
# Список типов принтеров
available_printer_sizes = ["маленький", "большой", "старый", "новый"]
# Список отделов в мфц
available_groups_in_mfc = ["юристы", "кадры", "бухгалтерия", "окна", "другой отдел"]
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

# Конструктор класса принтеров
class OrderPrinter(StatesGroup):
    waiting_for_printer_problem = State()
    waiting_for_other_printer_problem = State()
    waiting_for_unknown_printer_name = State()
    waiting_for_printer_name = State()
    waiting_for_printer_size = State()
    waiting_available_group_in_mfc = State()
    waiting_for_window = State()

# Начало работы с принтером
async def printer_start(message: types.Message):
    # Создаем кнопки с проблемами о принтерах
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_printer_problems:
        keyboard.add(name)
    await message.answer("🖨️ Какая у вас проблема с принтером?", reply_markup=keyboard)
    # Ожидание следующего состояния
    await OrderPrinter.waiting_for_printer_problem.set()

# Выбор проблемы с принтером
async def printer_problem_chosen(message: types.Message, state: FSMContext):
    # Вариант с клавиатуры или если сработали регулярные выражения
    if message.text.lower() in available_printer_problems or re.match(regexp_printer, message.text.lower()):
        # Если выбрана другая проблема
        if message.text.lower() == available_printer_problems[len(available_printer_problems) - 1].lower():
            print("other")
            # Бот показывает сообщение пользователю
            await message.answer("⚠ Пожалуйста, напишите проблему, которая у вас случилась с принтером:",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает состояние принтера с другой проблемой
            await OrderPrinter.waiting_for_other_printer_problem.set()
        else:  # Если выбрана конкретная проблема
            print("yes i know my problem with printer")
            # Добавляем в хранилище данных информацию о проблеме
            await state.update_data(chosen_printer_problem=message.text.lower())
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) # Создание клавиатуры
            # for name in available_printer_names:
            #     keyboard.add(name)
            # Расстановка клавиатуры в ряд
            keyboard.row(available_printer_names[0], available_printer_names[1])
            keyboard.row(available_printer_names[2], available_printer_names[3])
            keyboard.row(available_printer_names[4], available_printer_names[5])
            keyboard.row(available_printer_names[6])
            keyboard.row(available_printer_names[7])
            # Бот ожидает следующее состояние - модель принтера
            await OrderPrinter.waiting_for_printer_name.set()
            # После нажатии на кнопку, бот попросит выбрать модель принтера
            await message.answer("⚠ Пожалуйста, выберите ваш принтер:", reply_markup=keyboard)
    # Если текст не в списке кнопок, или не сработали регулярные выражения
    elif message.text.lower() not in available_printer_problems:
        # Бот просит выбрать один из вариантов
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        # Создать кнопки с наименованием проблем с принтерами
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_printer_problems:
            keyboard.add(name)
        # Бот спрашивает пользователя, в чём его проблема
        await message.answer("🖨️ Какая у вас проблема с принтером?", reply_markup=keyboard)
        return

# Функция для выбора другой проблемы о принтере
async def printer_other_problem_chosen(message: types.Message, state: FSMContext):
    # Записываем информацию во временное хранилище о выбранной проблеме
    await state.update_data(chosen_printer_problem=message.text.lower())
    # Создаем клавиатуру (кнопки)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for name in available_printer_names:
    #     keyboard.add(name)
    # Расставляем кнопки в ряд
    keyboard.row(available_printer_names[0], available_printer_names[1])
    keyboard.row(available_printer_names[2], available_printer_names[3])
    keyboard.row(available_printer_names[4], available_printer_names[5])
    keyboard.row(available_printer_names[6])
    keyboard.row(available_printer_names[7])
    # Бот ожидает следующее состояние с моделями принтера
    await OrderPrinter.waiting_for_printer_name.set()
    # Бот предлагает выбрать пользователю модель принтера
    await message.answer("⚠ Пожалуйста, выберите ваш принтер:", reply_markup=keyboard)


# Функция для выбора принтера
async def printer_chosen(message: types.Message, state: FSMContext):
    # Если выбрали вариант не с кнопки
    if message.text.lower() not in available_printer_names:
        # Бот предложит выбрать вариант с кнопки
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже.")
        return
    # Если выбран вариант с кнопки
    if message.text.lower() in available_printer_names:
        # Если выбрана неизвестная модель принтера
        if message.text.lower() == available_printer_names[len(available_printer_names) - 2].lower():
            print("unknown model")
            # Бот ожидает следующее состояние
            await OrderPrinter.waiting_for_unknown_printer_name.set()
            # Бот предлагает написать название принтера
            await message.answer("⚠ Пожалуйста, напишите название модели принтера", reply_markup=types.ReplyKeyboardRemove())
        # Иначе, если выбрано другая модель принтера
        elif message.text.lower() == available_printer_names[len(available_printer_names) - 1]:
            print("other")
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # for size in available_printer_sizes:
            #     keyboard.add(size)
            # Расстановка кнопок в ряд
            keyboard.row(available_printer_sizes[0], available_printer_sizes[1])
            keyboard.row(available_printer_sizes[2], available_printer_sizes[3])
            # Бот ожидает следующее состояние - размер принтеров
            await OrderPrinter.waiting_for_printer_size.set()
            # Бот предлагает написать описание принтера
            await message.answer("⚠ Пожалуйста, напишите описание принтера:", reply_markup=keyboard)
        # Иначе, если выбрана модель
        else:
            print("chosen model")
            # Добавить во временное хранилище информацию о модели принтера
            await state.update_data(chosen_printer=message.text.lower())
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # for size in available_groups_in_mfc:
            #     keyboard.add(size)
            # Расстановка кнопок в ряд
            keyboard.row(available_groups_in_mfc[0], available_groups_in_mfc[1])
            keyboard.row(available_groups_in_mfc[2], available_groups_in_mfc[3])
            keyboard.row(available_groups_in_mfc[4])
            # Бот ожидает следующее состояние с отделами мфц
            await OrderPrinter.waiting_available_group_in_mfc.set()
            # Бот предлагает выбрать отдел
            await message.answer("⚠ Теперь укажите ваш отдел...", reply_markup=keyboard)

# Функция для отображения неизвестной модели принтера
async def unknown_model_printer(message: types.Message, state: FSMContext):
    # Добавляем во временное хранилище информацию о написанной модели
    await state.update_data(chosen_printer=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Расстановка кнопок в ряд
    keyboard.row(available_groups_in_mfc[0], available_groups_in_mfc[1])
    keyboard.row(available_groups_in_mfc[2], available_groups_in_mfc[3])
    keyboard.row(available_groups_in_mfc[4])
    # for size in available_groups_in_mfc:
    #     keyboard.row(size)
    # Бот ожидает следующее состояние - выбор отделов мфц
    await OrderPrinter.waiting_available_group_in_mfc.set()
    # Бот предлагает выбрать отдел
    await message.answer("⚠ Теперь укажите ваш отдел...", reply_markup=keyboard)

# Функция для отображения размеров принтеров
async def printer_size_chosen(message: types.Message, state: FSMContext):
    # Если выбран вариант не с клавиатуры
    if message.text.lower() not in available_printer_sizes:
        await message.answer("⚠ Пожалуйста, выберите описание принтера, используя клавиатуру ниже. ⚠")
        return
    # Добавим во временное хранилище информацию о выбранном принтере
    await state.update_data(chosen_printer=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for size in available_groups_in_mfc:
    #     keyboard.add(size)
    # Расстановка кнопок в ряд
    keyboard.row(available_groups_in_mfc[0], available_groups_in_mfc[1])
    keyboard.row(available_groups_in_mfc[2], available_groups_in_mfc[3])
    keyboard.row(available_groups_in_mfc[4])
    # Бот ожидает следующее состояние с выбором отделов мфц
    await OrderPrinter.waiting_available_group_in_mfc.set()
    # Бот предлагает выбрать отдел
    await message.answer("⚠ Теперь укажите ваш отдел...", reply_markup=keyboard)

# Функция для выбора отделов мфц
async def group_in_mfc_chosen(message: types.Message, state: FSMContext):
    # Если выбран вариант не с кнопки
    if message.text.lower() not in available_groups_in_mfc:
        await message.answer("⚠ Пожалуйста, выберите ваш отдел, используя клавиатуру ниже. ⚠")
        return
    # Если выбраны окна
    if message.text.lower() == "окна":
        # Добавить во временное хранилище выбранную информацию
        await state.update_data(chosen_window_mfc=message.text.lower())
        # Бот ожидает следующее состояния - выбор окна
        await OrderPrinter.waiting_for_window.set()
        # Бот предлагает выбрать окно
        await message.answer("⚠ Укажите ваше окно...", reply_markup=types.ReplyKeyboardRemove())
    # Если выбран другой вариант
    else:
        # Добавить во временное хранилище информацию об отделе
        await state.update_data(chosen_group_mfc=message.text.lower())
        # Считать временное хранилище
        user_data = await state.get_data()
        # Текст для ответа пользователю
        answer_text = f"🖨️ С вашим принтером такая проблема: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                      f"Ваш принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {user_data['chosen_group_mfc'].upper()}.\n" \
                      "⛹ IT-специалист скоро подойдет к вам.  Ожидайте..."
        # Текст для ответа в группу мфц
        answer_to_group = f"🖨️ Проблема с принтером: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                          f"Принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {message.text.upper()}.\n" \
                          "Требуют айтишника! 🚀🚀🚀\n"
        # Бот отвечает информацию пользователю
        await message.answer(answer_text, reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот пересылает сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
        # Бот присылает подробную информацию с обращением по принтеру в группу
        return SendMessage(admin_group_id, answer_to_group)

# Функция для выбора окна
async def window_chosen(message: types.Message, state: FSMContext):
    # Считать данные со временного хранилища
    user_data = await state.get_data()
    # Ответ пользователю
    answer_text = f"🖨️ С вашим принтером такая проблема: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                  f"Ваш принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {message.text.upper()}.\n" \
                  "⛹ IT-специалист скоро подойдет к вам.  Ожидайте..."
    # Ответ в группу
    answer_to_group = f"🖨️ Проблема с принтером: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                      f"Принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {message.text.upper()}.\n" \
                      "Требуют айтишника! 🚀🚀🚀\n"
    # Бот отсылает информацию пользователю
    await message.answer(answer_text, reply_markup=types.ReplyKeyboardRemove())
    # Бот предлагает выбрать другие функции
    await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    # Бот пересылает сообщение в группу
    await message.forward(admin_group_id)
    # Бот завершает состояние
    await state.finish()
    # Бот присылает подробную информацию с обращением по принтеру в группу
    return SendMessage(admin_group_id, answer_to_group)

# Установка хэндлеров для принтеров (перехватывают сообщения)
def register_handlers_printer(dp: Dispatcher):
    # Хэндлер для команды для начала работы с принтером
    dp.register_message_handler(printer_start, commands="printer", state="*")
    # Хэндлер для выбора проблемы с принтером
    dp.register_message_handler(printer_problem_chosen, state=OrderPrinter.waiting_for_printer_problem)
    # Хэндлер для выбора других проблем
    dp.register_message_handler(printer_other_problem_chosen, state=OrderPrinter.waiting_for_other_printer_problem)
    # Хэндлер для выбранного принтера
    dp.register_message_handler(printer_chosen, state=OrderPrinter.waiting_for_printer_name)
    # Хэндлер , если выбран неизвестная модель принтера
    dp.register_message_handler(unknown_model_printer, state=OrderPrinter.waiting_for_unknown_printer_name)
    # Хэндлер, если выбран тип принтера
    dp.register_message_handler(printer_size_chosen, state=OrderPrinter.waiting_for_printer_size)
    # Хэндлер для выбора отделов мфц
    dp.register_message_handler(group_in_mfc_chosen, state=OrderPrinter.waiting_available_group_in_mfc)
    # Хэндлер для выбора окна мфц
    dp.register_message_handler(window_chosen, state=OrderPrinter.waiting_for_window)
    # Поиск через регулярные выражения
    dp.register_message_handler(printer_problem_chosen, regexp=regexp_printer, state="*")
    # Хэндлер, если написать принтер. Перехватывает через регулярные выражения
    dp.register_message_handler(printer_start, regexp=".*принтер.*", state="*")

