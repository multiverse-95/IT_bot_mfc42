# Импорт библиотек для бота
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# Импорт конфигурационного файла
from fsm.app.config_reader import load_config
from aiogram.types import ParseMode
# Получение данных с конфигурационного файла
config = load_config("config/bot.ini")
# Получение id админ группы
admin_group_id = int(config.tg_bot.admin_group_id)
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
# Класс для других команд
class OtherCommands(StatesGroup):
    waiting_for_unknown_command = State()

# Функция для отображения неизвестной команды
async def unknown_comand(message: types.Message, state: FSMContext):
    # Завершить состояние
    await state.finish()
    # Бот сообщает, что не понял запрос
    await message.answer("❌ <b>Извините, я не понял ваш запрос...</b>", parse_mode=ParseMode.HTML)
    # Бот предлагает выбрать доступные команды
    await message.answer(html_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)

# Регистрация хэндлеров для других команд
def register_handlers_other_commands(dp: Dispatcher):
    # Хэндлер для других команд
    dp.register_message_handler(unknown_comand, regexp=".*", state="*")
