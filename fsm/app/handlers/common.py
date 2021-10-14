# Импорт библиотек для бота
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.types import ParseMode

# Функция для начала работы с ботом
async def cmd_start(message: types.Message, state: FSMContext):
    # Завершить состояние
    await state.finish()
    # Текст приветствия
    html_text = "🖐 Добро пожаловать! Я бот-айтишник! Как я вам могу помочь?\n" \
              "<b>Доступны следующие команды:</b>\n" \
              "/start - 🔑 начало работы бота \n" \
              "/help - ❓ помощь по боту \n" \
              "<b>АИС, ПК ПВД, 1C, Очередь</b> \n" \
              "/ais - 🖥️ вопросы по АИС \n" \
              "/pkpvd - 📋 вопросы по ПК ПВД \n" \
              "/1c - 📚 вопросы по 1C \n" \
              "/queue - ⏳ вопросы по очереди \n" \
              "<b>Техника и другое</b> \n" \
              "/printer - 🖨️ вопросы по принтеру \n" \
              "/cancel - 🚫 отменить текущее действие "
    # Бот отсылает текст с приветствием
    await message.answer(
        html_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
    )

# Функция для отображении помощи по боту
async def cmd_help(message: types.Message, state: FSMContext):
    # Завершить состояние
    await state.finish()
    # Текст сообщения
    html_text = "<b>Доступны следующие команды:</b>\n" \
                "/start - 🔑 начало работы бота \n" \
                "/help - ❓ помощь по боту \n" \
                "<b>АИС, ПК ПВД, 1C, Очередь</b> \n" \
                "/ais - 🖥️ вопросы по АИС \n" \
                "/pkpvd - 📋 вопросы по ПК ПВД \n" \
                "/1c - 📚 вопросы по 1C \n" \
                "/queue - ⏳ вопросы по очереди \n" \
                "<b>Техника и другое</b> \n" \
                "/printer - 🖨️ вопросы по принтеру \n" \
                "/cancel - 🚫 отменить текущее действие "
    # Бот отсылает текст сообщения пользователю
    await message.answer(html_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
    )

# Функция для отмены какого-либо действия
async def cmd_cancel(message: types.Message, state: FSMContext):
    # Завершить состояние
    await state.finish()
    # Бот сообщает, что действие отменено
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())

# Регистрация хендлеров
def register_handlers_common(dp: Dispatcher):
    # Хендлер для команды start
    dp.register_message_handler(cmd_start, commands="start", state="*")
    # Хендлер для команды help
    dp.register_message_handler(cmd_help, commands="help", state="*")
    # Хендлер для команды cancel
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    # dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
