from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fsm.app.config_reader import load_config
from aiogram.types import ParseMode

config = load_config("config/bot.ini")
admin_group_id = int(config.tg_bot.admin_group_id)

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

class OtherCommands(StatesGroup):
    waiting_for_unknown_command = State()


async def unknown_comand(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ <b>Извините, я не понял ваш запрос...</b>", parse_mode=ParseMode.HTML)
    await message.answer(html_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)



def register_handlers_other_commands(dp: Dispatcher):
    dp.register_message_handler(unknown_comand, regexp=".*", state="*")
