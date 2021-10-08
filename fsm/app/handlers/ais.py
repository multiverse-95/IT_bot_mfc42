import requests
import json
import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fsm.app.admin_authorization.ais_authorization_admin import AisAuthorization
# Если запускать через консоль, то использовать строку ниже
# from app.admin_authorization.ais_authorization_admin import AisAuthorization
from fsm.app.config_reader import load_config
from aiogram.types import ParseMode

config = load_config("config/bot.ini")
admin_group_id = int(config.tg_bot.admin_group_id)

available_ais_problems = ["проблема с АИС", "проблема с заявлением в АИС"]
available_ais_errors = {
    'RejectionReasonCode: NO_DATA RejectionReasonDescription:': 'Вы загрузили файл слишком большого размера. Попробуйте загрузить файл меньшего размера.',
    'Question2': 'answer2',
    'Question3': 'answer3'
    }

other_functions = "<i>Попробуйте другие функции:</i> \n" \
                  "<b>АИС, ПК ПВД, 1C, Очередь</b> \n" \
                  "/ais - 🖥️ вопросы по АИС \n" \
                  "/pkpvd - 📋 вопросы по ПК ПВД \n" \
                  "/1c - 📚 вопросы по 1C \n" \
                  "/queue - ⏳ вопросы по очереди \n" \
                  "<b>Техника и другое</b> \n" \
                  "/printer - 🖨️ вопросы по принтеру \n" \
                  "/cancel - 🚫 отменить текущее действие "

class OrderAis(StatesGroup):
    waiting_for_ais_problem = State()
    waiting_for_other_ais_problem = State()
    waiting_for_ais_request_problem = State()
    waiting_for_ais_request_problem_try_again = State()


async def ais_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_ais_problems)
    # for name in available_ais_problems:
    #     keyboard.add(name)
    await message.answer("🖥️ Какая у вас проблема с АИС? ", reply_markup=keyboard)
    await OrderAis.waiting_for_ais_problem.set()


async def ais_problem_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_ais_problems:
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        return
    if message.text in available_ais_problems:
        if message.text == available_ais_problems[len(available_ais_problems) - 1]:
            await state.update_data(chosen_ais_request_problem=message.text.lower())
            await message.answer("⚠ Пожалуйста, напишите ваш номер заявления \n❗ (ТОЛЬКО ЦИФРЫ)",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderAis.waiting_for_ais_request_problem.set()
        else:
            await message.answer("⚠ Пожалуйста, напишите проблему, которая у вас случилась с АИС. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderAis.waiting_for_other_ais_problem.set()


async def ais_other_problem_chosen(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        answer_to_group = f"🖥️ ⚠ Проблема с АИС..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    elif message.content_type == 'photo':
        answer_to_group = f"🖥️ ⚠ Проблема с АИС..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    elif message.content_type == 'text':
        print("test text")
        await state.update_data(chosen_ais_problem=message.text.lower())
        user_data = await state.get_data()
        answer_to_message = f"⚠ У вас текущая проблема с АИС: {user_data['chosen_ais_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        answer_to_group = f"🖥️ ⚠ Проблема с АИС: {user_data['chosen_ais_problem'].lower()}"
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    # return SendMessage(admin_group_id, answer_to_group)


async def ais_request_problem(message: types.Message, state: FSMContext):
    await message.answer("⚠ ⏱️ Подождите, ищу решение проблемы...",
                         reply_markup=types.ReplyKeyboardRemove())
    ais_author = AisAuthorization()
    cookie_ais = await ais_author.read_cookie_from_file()
    isCookieValid = await ais_author.check_if_cookie_valid(cookie_ais)
    if not isCookieValid:
        cookie_ais = await ais_author.admin_authorization()
        await ais_author.save_data_to_file(cookie_ais)
    # numberreq = '7303506'
    number_of_req = message.text
    payload = {"action": "orderService", "method": "getOrderHistory", "data": [number_of_req, False], "type": "rpc",
               "tid": 23}
    response = requests.post(
        'http://192.168.99.91/cpgu/action/router',
        headers={'Cookie': 'JSESSIONID='+cookie_ais},
        json=payload)

    resp_json = response.text
    parsed_string = json.loads(resp_json)
    print("JSON: ", parsed_string)

    request_not_found = '⚠ Заявление не удалось найти. Проверьте номер заявления...'
    json_type = parsed_string[0]['type']
    if json_type == 'rpc':
        result = parsed_string[0]['result']
        result_size = len(result)
        error_text = parsed_string[0]['result'][result_size - 1]['comment']
        fix_not_found = 'К сожалению, решение не удалось найти. Попробуйте пересоздать заявление, правильно заполните все поля и попробуйте снова.\n' \
                        'Если ошибка не исчезнет, тогда позвоните в IT-отдел'

        list_code_errors = list(available_ais_errors.keys())
        # print(list_code_errors[0])
        solveError = 'Not solved'
        for i in range(len(available_ais_errors)):
            print('\n' + 'Ошибка: ' + list_code_errors[i])
            result_re = re.match(list_code_errors[i], error_text)
            if result_re is None:
                print('Not found')
            else:
                print('Совпадение с ошибкой: ' + result_re.group(0))
                solveError = available_ais_errors[list_code_errors[i]]
                break

        if solveError == 'Not solved':
            print('Решение не найдено...')
            await message.answer(fix_not_found)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('да', 'нет')
            await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
            await OrderAis.waiting_for_ais_request_problem_try_again.set()
        else:
            print('Как решить: ' + solveError)
            await message.answer(solveError)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('да', 'нет')
            await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
            await OrderAis.waiting_for_ais_request_problem_try_again.set()

    elif json_type == 'exception':
        await message.answer(request_not_found)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('да', 'нет')
        await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
        await OrderAis.waiting_for_ais_request_problem_try_again.set()



async def ais_request_problem_try_again(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        #await state.update_data(chosen_ais_request_problem=message.text.lower())
        await message.answer("⚠ Пожалуйста, напишите ваш номер заявления \n❗ (ТОЛЬКО ЦИФРЫ)",
                             reply_markup=types.ReplyKeyboardRemove())
        await OrderAis.waiting_for_ais_request_problem.set()
    elif message.text.lower() == 'нет':
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await state.finish()
    else:
        await message.answer("⚠ Пожалуйста, выберите вариант из клавиатуры ниже\n"
                             "Побробовать ещё раз?")


def register_handlers_ais(dp: Dispatcher):
    dp.register_message_handler(ais_start, commands="ais", state="*")
    dp.register_message_handler(ais_problem_chosen, state=OrderAis.waiting_for_ais_problem)
    dp.register_message_handler(ais_request_problem, state=OrderAis.waiting_for_ais_request_problem)
    dp.register_message_handler(ais_request_problem_try_again, state=OrderAis.waiting_for_ais_request_problem_try_again)
    dp.register_message_handler(ais_other_problem_chosen, content_types=types.ContentType.all(), state=OrderAis.waiting_for_other_ais_problem)
