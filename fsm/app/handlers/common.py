from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.types import ParseMode


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
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
    await message.answer(
        html_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
    )


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
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
    await message.answer(html_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_help, commands="help", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    # dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
