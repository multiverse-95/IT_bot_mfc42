import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Эти значения далее будут подставляться в итоговый текст
from aiogram.dispatcher.webhook import SendMessage
from aiogram.types import ParseMode

from fsm.app.config_reader import load_config

config = load_config("config/bot.ini")
admin_group_id = int(config.tg_bot.admin_group_id)

# Данные о принтерах
regexp_printer = '.*картридж.*|.*тонер.*|.*чернил.*|.*не.*работ.*|.*не.*печат.*|.*ломалс.*'
available_printer_problems = ["картридж закончился", "плохо печатает", "не печатает", "другая проблема"]
available_printer_names = ["1025", "2540", "2235", "2035", "2530", "1030", "другая модель", "не могу определить модель"]
available_printer_sizes = ["маленький", "большой", "старый", "новый"]
available_groups_in_mfc = ["юристы", "кадры", "бухгалтерия", "окна", "другой отдел"]

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
    # Вариант с клавиатуры
    if message.text.lower() in available_printer_problems or re.match(regexp_printer, message.text.lower()):
        # Если выбрана другая проблема
        if message.text.lower() == available_printer_problems[len(available_printer_problems) - 1].lower():
            print("other")
            await message.answer("⚠ Пожалуйста, напишите проблему, которая у вас случилась с принтером:",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderPrinter.waiting_for_other_printer_problem.set()
        else:  # Если выбрана конкретная проблема
            print("yes i know my problem with printer")
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
            # Ожидаем следующее состояние
            await OrderPrinter.waiting_for_printer_name.set()
            # После нажатии на кнопку, бот попросит выбрать модель принтера
            await message.answer("⚠ Пожалуйста, выберите ваш принтер:", reply_markup=keyboard)

    elif message.text.lower() not in available_printer_problems:
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        return

# Функция для выбора другой проблемы о принтере
async def printer_other_problem_chosen(message: types.Message, state: FSMContext):
    # Записываем информацию во временное хранилище
    await state.update_data(chosen_printer_problem=message.text.lower())
    # Создаем клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for name in available_printer_names:
    #     keyboard.add(name)
    keyboard.row(available_printer_names[0], available_printer_names[1])
    keyboard.row(available_printer_names[2], available_printer_names[3])
    keyboard.row(available_printer_names[4], available_printer_names[5])
    keyboard.row(available_printer_names[6])
    keyboard.row(available_printer_names[7])
    # Ожидаем следующее состояние
    await OrderPrinter.waiting_for_printer_name.set()
    # Предлагаем выбрать пользователю модель принтера
    await message.answer("⚠ Пожалуйста, выберите ваш принтер:", reply_markup=keyboard)


# Функция для выбора принтера
async def printer_chosen(message: types.Message, state: FSMContext):
    # Если выбрали вариант не с кнопки
    if message.text.lower() not in available_printer_names:
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже.")
        return
    # Если выбран вариант с кнопки
    if message.text.lower() in available_printer_names:
        if message.text.lower() == available_printer_names[len(available_printer_names) - 2].lower():
            print("unknown model")
            await OrderPrinter.waiting_for_unknown_printer_name.set()
            await message.answer("⚠ Пожалуйста, напишите название модели принтера", reply_markup=types.ReplyKeyboardRemove())
        elif message.text.lower() == available_printer_names[len(available_printer_names) - 1]:
            print("other")
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # for size in available_printer_sizes:
            #     keyboard.add(size)
            keyboard.row(available_printer_sizes[0], available_printer_sizes[1])
            keyboard.row(available_printer_sizes[2], available_printer_sizes[3])
            await OrderPrinter.waiting_for_printer_size.set()
            await message.answer("⚠ Пожалуйста, напишите описание принтера:", reply_markup=keyboard)
        else:
            print("chosen model")
            await state.update_data(chosen_printer=message.text.lower())
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # for size in available_groups_in_mfc:
            #     keyboard.add(size)
            keyboard.row(available_groups_in_mfc[0], available_groups_in_mfc[1])
            keyboard.row(available_groups_in_mfc[2], available_groups_in_mfc[3])
            keyboard.row(available_groups_in_mfc[4])
            await OrderPrinter.waiting_available_group_in_mfc.set()
            await message.answer("⚠ Теперь укажите ваш отдел...", reply_markup=keyboard)


async def unknown_model_printer(message: types.Message, state: FSMContext):
    await state.update_data(chosen_printer=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(available_groups_in_mfc[0], available_groups_in_mfc[1])
    keyboard.row(available_groups_in_mfc[2], available_groups_in_mfc[3])
    keyboard.row(available_groups_in_mfc[4])
    # for size in available_groups_in_mfc:
    #     keyboard.row(size)
    await OrderPrinter.waiting_available_group_in_mfc.set()
    await message.answer("⚠ Теперь укажите ваш отдел...", reply_markup=keyboard)


async def printer_size_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_printer_sizes:
        await message.answer("⚠ Пожалуйста, выберите описание принтера, используя клавиатуру ниже. ⚠")
        return
    await state.update_data(chosen_printer=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for size in available_groups_in_mfc:
    #     keyboard.add(size)
    keyboard.row(available_groups_in_mfc[0], available_groups_in_mfc[1])
    keyboard.row(available_groups_in_mfc[2], available_groups_in_mfc[3])
    keyboard.row(available_groups_in_mfc[4])
    await OrderPrinter.waiting_available_group_in_mfc.set()
    await message.answer("⚠ Теперь укажите ваш отдел...", reply_markup=keyboard)


async def group_in_mfc_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_groups_in_mfc:
        await message.answer("⚠ Пожалуйста, выберите ваш отдел, используя клавиатуру ниже. ⚠")
        return
    if message.text.lower() == "окна":
        await state.update_data(chosen_window_mfc=message.text.lower())
        await OrderPrinter.waiting_for_window.set()
        await message.answer("⚠ Укажите ваше окно...", reply_markup=types.ReplyKeyboardRemove())
    else:
        await state.update_data(chosen_group_mfc=message.text.lower())
        user_data = await state.get_data()
        answer_text = f"🖨️ С вашим принтером такая проблема: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                      f"Ваш принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {user_data['chosen_group_mfc'].upper()}.\n" \
                      "⛹ IT-специалист скоро подойдет к вам.  Ожидайте..."
        answer_to_group = f"🖨️ Проблема с принтером: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                          f"Принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {message.text.upper()}.\n" \
                          "Требуют айтишника! 🚀🚀🚀\n"
        await message.answer(answer_text, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.forward(admin_group_id)
        await state.finish()
        return SendMessage(admin_group_id, answer_to_group)


async def window_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    answer_text = f"🖨️ С вашим принтером такая проблема: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                  f"Ваш принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {message.text.upper()}.\n" \
                  "⛹ IT-специалист скоро подойдет к вам.  Ожидайте..."
    answer_to_group = f"🖨️ Проблема с принтером: \"{user_data['chosen_printer_problem'].lower()}\".\n" \
                      f"Принтер: {user_data['chosen_printer'].upper()}, окно/отдел: {message.text.upper()}.\n" \
                      "Требуют айтишника! 🚀🚀🚀\n"
    await message.answer(answer_text, reply_markup=types.ReplyKeyboardRemove())
    await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    await message.forward(admin_group_id)
    await state.finish()
    return SendMessage(admin_group_id, answer_to_group)


def register_handlers_printer(dp: Dispatcher):
    # Работа с командами бота
    dp.register_message_handler(printer_start, commands="printer", state="*")
    dp.register_message_handler(printer_problem_chosen, state=OrderPrinter.waiting_for_printer_problem)
    dp.register_message_handler(printer_other_problem_chosen, state=OrderPrinter.waiting_for_other_printer_problem)
    dp.register_message_handler(printer_chosen, state=OrderPrinter.waiting_for_printer_name)
    dp.register_message_handler(unknown_model_printer, state=OrderPrinter.waiting_for_unknown_printer_name)
    dp.register_message_handler(printer_size_chosen, state=OrderPrinter.waiting_for_printer_size)
    dp.register_message_handler(group_in_mfc_chosen, state=OrderPrinter.waiting_available_group_in_mfc)
    dp.register_message_handler(window_chosen, state=OrderPrinter.waiting_for_window)
    # Поиск через регулярные выражения
    dp.register_message_handler(printer_problem_chosen, regexp=regexp_printer, state="*")
    dp.register_message_handler(printer_start, regexp=".*принтер.*", state="*")

