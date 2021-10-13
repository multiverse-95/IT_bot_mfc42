from aiogram import Dispatcher, types
import re
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fsm.app.config_reader import load_config
from aiogram.types import ParseMode

config = load_config("config/bot.ini")
admin_group_id = int(config.tg_bot.admin_group_id)
regexp_1c = '(\W|^).*1с.*завис.*(\W|$)|(\W|^).*завис.*1с(\W|$)|(\W|^).*не\sработ.*1с(\W|$)|(\W|^).*1с.*не\sработ.*(\W|$)' \
            '|(\W|^).*1с.*весит(\W|$)|(\W|^).*1с.*висит.*(\W|$)|(\W|^).*весит.*1с(\W|$)|(\W|^).*висит.*1с(\W|$)|(\W|^).*1с.*почин.*(\W|$)|(\W|^).*почин.*1с(\W|$)'
available_buh_1C_problems = ["Не работает/завис 1С", "Другая проблема с 1С"]
other_functions = "<i>Попробуйте другие функции:</i> \n" \
                  "<b>АИС, ПК ПВД, 1C, Очередь</b> \n" \
                  "/ais - 🖥️ вопросы по АИС \n" \
                  "/pkpvd - 📋 вопросы по ПК ПВД \n" \
                  "/1c - 📚 вопросы по 1C \n" \
                  "/queue - ⏳ вопросы по очереди \n" \
                  "<b>Техника и другое</b> \n" \
                  "/printer - 🖨️ вопросы по принтеру \n" \
                  "/cancel - 🚫 отменить текущее действие "

class OrderBuh1C(StatesGroup):
    waiting_for_buh_1C_problem = State()
    waiting_for_other_buh_1C_problem = State()


async def buh_1C_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_buh_1C_problems)
    # for name in available_buh_1C_problems:
    #     keyboard.add(name)
    await message.answer("📚 Какая у вас проблема с 1С? ", reply_markup=keyboard)
    await OrderBuh1C.waiting_for_buh_1C_problem.set()


async def buh_1C_problem_chosen(message: types.Message, state: FSMContext):
    if message.text in available_buh_1C_problems or re.match(regexp_1c, message.text.lower()):
        if message.text == available_buh_1C_problems[len(available_buh_1C_problems) - 1]:
            await state.update_data(chosen_buh_1C_problem=message.text.lower())
            await message.answer("⚠ Пожалуйста, напишите вашу проблему с 1С. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderBuh1C.waiting_for_other_buh_1C_problem.set()
        else:
            await state.update_data(chosen_buh_1C_server_problem=message.text.lower())
            await message.answer("⚠ Сервер 1С будет перезагружен. Пожалуйста, подождите 5 минут...",
                                 reply_markup=types.ReplyKeyboardRemove())
            user_data = await state.get_data()
            answer_to_group = f"📚 ⚠ Проблема с 1С: {user_data['chosen_buh_1C_server_problem'].lower()}"
            await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
            await message.bot.send_message(admin_group_id, answer_to_group)
            await message.forward(admin_group_id)
            await state.finish()
    elif message.text not in available_buh_1C_problems:
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_buh_1C_problems)
        await message.answer("📚 Какая у вас проблема с 1С? ", reply_markup=keyboard)
        return


async def buh_1C_other_problem_chosen(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        answer_to_group = f"📚 ⚠ Проблема с 1С..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    elif message.content_type == 'photo':
        answer_to_group = f"📚 ⚠ Проблема с 1С..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    elif message.content_type == 'text':
        await state.update_data(chosen_buh_1C_problem=message.text.lower())
        user_data = await state.get_data()
        answer_to_message = f"⚠ У вас текущая проблема с 1С: {user_data['chosen_buh_1C_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        answer_to_group = f"📚 ⚠ Проблема с 1С: {user_data['chosen_buh_1C_problem'].lower()}"
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()




def register_handlers_buh_1C(dp: Dispatcher):
    dp.register_message_handler(buh_1C_start, commands="1c", state="*")
    dp.register_message_handler(buh_1C_problem_chosen, state=OrderBuh1C.waiting_for_buh_1C_problem)
    dp.register_message_handler(buh_1C_other_problem_chosen, content_types=types.ContentType.all(), state=OrderBuh1C.waiting_for_other_buh_1C_problem)
    # Поиск через регулярные выражения
    dp.register_message_handler(buh_1C_problem_chosen, regexp=regexp_1c, state="*")
    dp.register_message_handler(buh_1C_start, regexp="(\W|^)1c.*(\W|$)|(\W|^)1с.*(\W|$)|(\W|^)один\s.с.*(\W|$)|(\W|^)1\s.с.*(\W|$)", state="*")

