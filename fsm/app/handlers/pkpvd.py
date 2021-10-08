import requests
import json
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fsm.app.admin_authorization.pkpvd_authorization_admin import PkpvdAuthorization
# Если запускать через консоль, то использовать строку ниже
# from app.pkpvd_authorization.pkpvd_authorization_admin import pkpvdAuthorization

from aiogram.types import ParseMode
from fsm.app.config_reader import load_config

config = load_config("config/bot.ini")
admin_group_id = int(config.tg_bot.admin_group_id)

available_pkpvd_problems = ["Не работает или зависает ПК ПВД", "Ошибка в обращении"]
available_pkpvd_errors = {
    'Duplicate unique value [usage Purpose] declared for identity constraint of element \"note Group\".':
        'Необходимо \n1.Найти прикрепленный объект и войти в меню изменение объекта, вручную очистить строку «назначение здания» (нажать на серый крестик)'
        '\n2.В дополнительной информации вручную прописать жилое или нежилое \n3.Выбрать вид разрешенного использования',
    'кириллица, недопустимые символы, "The value"': 'Неточно указана почта',
    'указан диапазон допустимых символов вида [1-0, a-Z, а-Я]': 'Некорректно заполнены поля',
    './doc:idPayer': 'В "Платёжных документах" не заполнено поле "Плательщик"',
    'acceptActionNotification':
        'В поле "Представление и получение документов" следует проверить типы уведомления заявителя и получения документов, обратить внимание на поля № телефона и адреса e-mail, если выбраны',
    'Duplicate key value [...] declared for identity constraint of element "statementFormChangeRegisteredStatement"':
        'В заявлении два заявителя',
    'cvc-pattern-valid: Value \'008002099000\' is not facet-valid with respect to pattern \'008001\d{6}\' for type':
        'сотрудник для документа выбрал тип "Иной документ"'
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


class OrderPkpvd(StatesGroup):
    waiting_for_pkpvd_problem = State()
    waiting_for_other_pkpvd_problem = State()
    waiting_for_pkpvd_request_problem = State()
    waiting_for_pkpvd_request_problem_try_again = State()


async def pkpvd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_pkpvd_problems)
    # for name in available_pkpvd_problems:
    #     keyboard.add(name)
    await message.answer("📋 Какая у вас проблема с ПК ПВД? ", reply_markup=keyboard)
    await OrderPkpvd.waiting_for_pkpvd_problem.set()


async def pkpvd_problem_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_pkpvd_problems:
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        return
    if message.text in available_pkpvd_problems:
        if message.text == available_pkpvd_problems[len(available_pkpvd_problems) - 1]:
            await state.update_data(chosen_pkpvd_request_problem=message.text.lower())
            await message.answer("⚠ Пожалуйста, напишите ваш номер обращения",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderPkpvd.waiting_for_pkpvd_request_problem.set()
        else:
            await message.answer("⚠ Пожалуйста, напишите проблему, которая у вас случилась с ПК ПВД. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            await OrderPkpvd.waiting_for_other_pkpvd_problem.set()


async def pkpvd_other_problem_chosen(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        answer_to_group = f"📋 ⚠ Проблема с ПК ПВД..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    elif message.content_type == 'photo':
        answer_to_group = f"📋 ⚠ Проблема с ПК ПВД..."
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    elif message.content_type == 'text':
        print("test text")
        await state.update_data(chosen_pkpvd_problem=message.text.lower())
        user_data = await state.get_data()
        answer_to_message = f"⚠ У вас текущая проблема с ПК ПВД: {user_data['chosen_pkpvd_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        answer_to_group = f"📋 ⚠ Проблема с ПК ПВД: {user_data['chosen_pkpvd_problem'].lower()}"
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await message.bot.send_message(admin_group_id, answer_to_group)
        await message.forward(admin_group_id)
        await state.finish()
    # return SendMessage(admin_group_id, answer_to_group)


async def pkpvd_request_problem(message: types.Message, state: FSMContext):
    await message.answer("⚠ ⏱️ Подождите, ищу решение проблемы...",
                         reply_markup=types.ReplyKeyboardRemove())
    pkpvd_author = PkpvdAuthorization()
    cookie_pkpvd = await pkpvd_author.read_cookie_from_file()
    isCookieValid = await pkpvd_author.check_if_cookie_valid(cookie_pkpvd)
    if not isCookieValid:
        cookie_pkpvd = await pkpvd_author.admin_authorization()
        await pkpvd_author.save_data_to_file(cookie_pkpvd)

    number_of_req = message.text.upper()
    responseAppeal = requests.get(
        'http://10.42.200.207/api/rs/appeal/search2?page=0&size=5&sort=createDate,desc&startWith=false&internalNum='+number_of_req+'&packageNum'
        '=&statusNotePPOZ=&currentStep=&createDateFrom=&createDateTill=&createWho=&moveStepDate=&kudNum=&routineExecutionDays=&processingEndDateFrom='
        '&processingEndDateTill=&typeGosUslug=&cn=&textApplicants=',
        headers={'Cookie': 'JSESSIONID=' + cookie_pkpvd})

    resp_json = responseAppeal.text
    parsed_string = json.loads(resp_json)
    if len(parsed_string['content']) == 0:
        await message.answer("Обращение не найдено.")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('да', 'нет')
        await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
        await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()
    else:
        id_appeal = parsed_string['content'][0]['id']
        print("JSON Appeal: ", parsed_string)

        responseStatement = requests.get('http://10.42.200.207/api/rs/appeal/' + id_appeal + '/statement?page=0&size=5',
                                         headers={'Cookie': 'JSESSIONID=' + cookie_pkpvd})

        resp_json = responseStatement.text
        parsed_string = json.loads(resp_json)
        id_statement = parsed_string['content'][0]['id']
        print("JSON Statement: ", parsed_string)

        responseFindErrror = requests.get(
            'http://10.42.200.207/api/rs/appeal/' + id_appeal + '/' + id_statement + '/printstatement',
            headers={'Cookie': 'JSESSIONID=' + cookie_pkpvd})

        resp_document = responseFindErrror.text
        # parsed_string = json.loads(resp_json)
        # print("JSON print document: ", resp_document)

        isDocError = True

        try:
            json.loads(resp_document)
        except ValueError as err:
            isDocError = False

        print('Документ с ошибкой? ' + str(isDocError))
        documentCorrect = "С вашим обращением всё в порядке."
        if isDocError:
            parsed_document_error = json.loads(resp_document)
            code_error = parsed_document_error['status']
            message_error = parsed_document_error['message']
            # message_error = 'Ошибка формирования XML-файла: Duplicate unique value [usage Purpose] declared for identity constraint of element \"note Group\". '
            fix_not_found = 'Решение не найдено'

            list_code_errors = list(available_pkpvd_errors.keys())
            # print(list_code_errors[0])
            solveError = 'Not solved'
            for i in range(len(available_pkpvd_errors)):
                print('\n' + 'Ошибка: ' + list_code_errors[i])
                index = message_error.find(list_code_errors[i])
                if index == -1:
                    print('Not found')
                else:
                    print('Совпадение с ошибкой: ' + available_pkpvd_errors[list_code_errors[i]])
                    solveError = available_pkpvd_errors[list_code_errors[i]]
                    break

            if solveError == 'Not solved':
                print('Решение не найдено...')
                await message.answer(fix_not_found)
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.row('да', 'нет')
                await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
                await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()
            else:
                print('Как решить: ' + solveError)
                await message.answer(solveError)
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.row('да', 'нет')
                await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
                await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()
        else:
            await message.answer(documentCorrect)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('да', 'нет')
            await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
            await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()



async def pkpvd_request_problem_try_again(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        # await state.update_data(chosen_pkpvd_request_problem=message.text.lower())
        await message.answer("⚠ Пожалуйста, напишите ваш номер обращения",
                             reply_markup=types.ReplyKeyboardRemove())
        await OrderPkpvd.waiting_for_pkpvd_request_problem.set()
    elif message.text.lower() == 'нет':
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await state.finish()
    else:
        await message.answer("⚠ Пожалуйста, выберите вариант из клавиатуры ниже\n"
                             "Побробовать ещё раз?")


def register_handlers_pkpvd(dp: Dispatcher):
    dp.register_message_handler(pkpvd_start, commands="pkpvd", state="*")
    dp.register_message_handler(pkpvd_problem_chosen, state=OrderPkpvd.waiting_for_pkpvd_problem)
    dp.register_message_handler(pkpvd_request_problem, state=OrderPkpvd.waiting_for_pkpvd_request_problem)
    dp.register_message_handler(pkpvd_request_problem_try_again, state=OrderPkpvd.waiting_for_pkpvd_request_problem_try_again)
    dp.register_message_handler(pkpvd_other_problem_chosen, content_types=types.ContentType.all(), state=OrderPkpvd.waiting_for_other_pkpvd_problem)

