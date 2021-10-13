from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from fsm.app.config_reader import load_config

config = load_config("config/bot.ini")
admin_group_id = int(config.tg_bot.admin_group_id)
regexp_queue = '(\W|^)очередь.*(\W|$)|(\W|^)проблема.*очеред.*(\W|$)|(\W|^)не\sработ.*очеред.*(\W|$)'
available_queue_problems = ["Завис талон", "Завис терминал", "Завис монитор", "Зависли кнопки", "Другая проблема с очередью"]
other_functions = "<i>Попробуйте другие функции:</i> \n" \
                  "<b>АИС, ПК ПВД, 1C, Очередь</b> \n" \
                  "/ais - 🖥️ вопросы по АИС \n" \
                  "/pkpvd - 📋 вопросы по ПК ПВД \n" \
                  "/1c - 📚 вопросы по 1C \n" \
                  "/queue - ⏳ вопросы по очереди \n" \
                  "<b>Техника и другое</b> \n" \
                  "/printer - 🖨️ вопросы по принтеру \n" \
                  "/cancel - 🚫 отменить текущее действие "

class OrderQueue(StatesGroup):
    waiting_for_queue_problem = State()
    waiting_for_queue_talon_problem = State()
    waiting_for_other_queue_problem = State()


async def queue_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for name in available_queue_problems:
    #     keyboard.add(name)
    keyboard.row(available_queue_problems[0], available_queue_problems[1])
    keyboard.row(available_queue_problems[2], available_queue_problems[3])
    keyboard.row(available_queue_problems[4])
    await message.answer("⏳ Какая у вас проблема с очередью? ", reply_markup=keyboard)
    await OrderQueue.waiting_for_queue_problem.set()


async def queue_problem_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_queue_problems:
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(available_queue_problems[0], available_queue_problems[1])
        keyboard.row(available_queue_problems[2], available_queue_problems[3])
        keyboard.row(available_queue_problems[4])
        await message.answer("⏳ Какая у вас проблема с очередью? ", reply_markup=keyboard)
        return
    if message.text in available_queue_problems:
        if message.text == available_queue_problems[len(available_queue_problems) - 1]:
            await state.update_data(chosen_queue_problem=message.text.lower())
            await message.answer("⚠ Пожалуйста, напишите вашу проблему с очередью. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderQueue.waiting_for_other_queue_problem.set()
        elif message.text == available_queue_problems[0]:
            await state.update_data(chosen_queue_problem=message.text.lower())
            await message.answer("⚠ Пожалуйста, прикрепите скриншот с зависшим талоном...",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderQueue.waiting_for_queue_talon_problem.set()
        else:
            await state.update_data(chosen_queue_problem=message.text.lower())
            await message.answer("⚠ Информация была выслана в IT-отдел",
                                 reply_markup=types.ReplyKeyboardRemove())
            user_data = await state.get_data()
            answer_to_group = f"⏳ ⚠ Проблема с очередью: {user_data['chosen_queue_problem'].lower()}"
            await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
            await message.bot.send_message(admin_group_id, answer_to_group)
            await message.forward(admin_group_id)
            await state.finish()



async def queue_other_problem_chosen(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        answer_to_group = f"⏳ ⚠ Проблема с очередью..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    elif message.content_type == 'photo':
        answer_to_group = f"⏳ ⚠ Проблема с очередью..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    elif message.content_type == 'text':
        print("test text")
        await state.update_data(chosen_queue_problem=message.text.lower())
        user_data = await state.get_data()
        answer_to_message = f"⚠ У вас текущая проблема с очередью: {user_data['chosen_queue_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        answer_to_group = f"⏳ ⚠ Проблема с очередью: {user_data['chosen_queue_problem'].lower()}"
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()

async def queue_talon_problem(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        answer_to_group = f"⏳ ⚠ Проблема с талоном в очереди... Надо что-то делать..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    elif message.content_type == 'photo':
        answer_to_group = f"⏳ ⚠ Проблема с талоном в очереди... Надо что-то делать..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    elif message.content_type == 'text':
        print("test text")
        await state.update_data(chosen_queue_problem=message.text.lower())
        user_data = await state.get_data()
        answer_to_message = f"⚠ У вас текущая проблема с очередью: {user_data['chosen_queue_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        answer_to_group = f"⏳ ⚠ Проблема с талоном в очереди... Надо что-то делать... {user_data['chosen_queue_problem'].lower()}"
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()




def register_handlers_queue(dp: Dispatcher):
    dp.register_message_handler(queue_start, commands="queue", state="*")
    dp.register_message_handler(queue_problem_chosen, state=OrderQueue.waiting_for_queue_problem)
    dp.register_message_handler(queue_talon_problem, content_types=types.ContentType.all(), state=OrderQueue.waiting_for_queue_talon_problem)
    dp.register_message_handler(queue_other_problem_chosen, content_types=types.ContentType.all(), state=OrderQueue.waiting_for_other_queue_problem)
    # Поиск через регулярные выражения
    dp.register_message_handler(queue_start, regexp=regexp_queue, state="*")

