# Импорт библиотек для работы с сетью и с json
import requests
import json
# Импорт библиотек для бота
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fsm.app.admin_authorization.pkpvd_authorization_admin import PkpvdAuthorization
# Если запускать через консоль, то использовать строку ниже
# from app.pkpvd_authorization.pkpvd_authorization_admin import pkpvdAuthorization

from aiogram.types import ParseMode
# Импорт конфигурационного файла
from fsm.app.config_reader import load_config
# Получение данных с конфигурационного файла
config = load_config("config/bot.ini")
# Получение id админ группы
admin_group_id = int(config.tg_bot.admin_group_id)
# Регулярные выражения для пк пвд
regexp_pkpvd = '.*пк\sпвд.*|.*пвд.*'
# Список проблем с пк пвд
available_pkpvd_problems = ["Не работает или зависает ПК ПВД", "Ошибка в обращении"]
# Словарь доступных ошибок и решений к ним
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

# Класс для работы с пк пвд
class OrderPkpvd(StatesGroup):
    waiting_for_pkpvd_problem = State()
    waiting_for_other_pkpvd_problem = State()
    waiting_for_pkpvd_request_problem = State()
    waiting_for_pkpvd_request_problem_try_again = State()

# Начало работы с пк пвд
async def pkpvd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_pkpvd_problems)
    # for name in available_pkpvd_problems:
    #     keyboard.add(name)
    await message.answer("📋 Какая у вас проблема с ПК ПВД? ", reply_markup=keyboard)
    await OrderPkpvd.waiting_for_pkpvd_problem.set()

# Функция для выбора проблемы с пк пвд
async def pkpvd_problem_chosen(message: types.Message, state: FSMContext):
    # Если выбран вариант не с кнопки
    if message.text not in available_pkpvd_problems:
        # Бот сообщит что нужно выбрать вариант с кнопки
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        # Создание кнопок с проблемаи пвд
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_pkpvd_problems)
        # Бот спрашивает про проблему с пвд
        await message.answer("📋 Какая у вас проблема с ПК ПВД? ", reply_markup=keyboard)
        return
    # Если пользователь выбрал из предложенных вариантов
    if message.text in available_pkpvd_problems:
        # Если выбрана проблема с обращением
        if message.text == available_pkpvd_problems[len(available_pkpvd_problems) - 1]:
            # Добавить данные во временное хранилище
            await state.update_data(chosen_pkpvd_request_problem=message.text.lower())
            # Бот предложит написать номер обращения
            await message.answer("⚠ Пожалуйста, напишите ваш номер обращения",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующего состояния с проблемой обращения
            await OrderPkpvd.waiting_for_pkpvd_request_problem.set()
        # Если выбран вариант с другой проблемой по пк пвд
        else:
            # Бот спросит о проблеме с пк пвд
            await message.answer("⚠ Пожалуйста, напишите проблему, которая у вас случилась с ПК ПВД. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующего состояния по другой проблеме с пк пвд
            await OrderPkpvd.waiting_for_other_pkpvd_problem.set()

# Функция для выбора других проблем с пк пвд
async def pkpvd_other_problem_chosen(message: types.Message, state: FSMContext):
    # Если пользователь прислал документ
    if message.content_type == 'document':
        # Ответ в группу
        answer_to_group = f"📋 ⚠ Проблема с ПК ПВД..."
        # Бот сообщает, что выслал в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    # Если пользователь прислал фотографию
    elif message.content_type == 'photo':
        # Ответ в группу
        answer_to_group = f"📋 ⚠ Проблема с ПК ПВД..."
        # Бот сообщает, что выслал в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
    # Если пользователь прислал текстовое сообщение
    elif message.content_type == 'text':
        print("test text")
        # Запись информации во временное хранилище
        await state.update_data(chosen_pkpvd_problem=message.text.lower())
        # Считывание информации с временного хранилища
        user_data = await state.get_data()
        # Ответ на сообщение
        answer_to_message = f"⚠ У вас текущая проблема с ПК ПВД: {user_data['chosen_pkpvd_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        # Ответ в группу
        answer_to_group = f"📋 ⚠ Проблема с ПК ПВД: {user_data['chosen_pkpvd_problem'].lower()}"
        # Бот отвечает на сообщение
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        # Бот предлагает выбрать другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправляет сообщение в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот пересылает сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершает состояние
        await state.finish()
    # return SendMessage(admin_group_id, answer_to_group)

# Функция для работы с номером обращения
async def pkpvd_request_problem(message: types.Message, state: FSMContext):
    # Бот сообщает, что ищет решение проблемы
    await message.answer("⚠ ⏱️ Подождите, ищу решение проблемы...",
                         reply_markup=types.ReplyKeyboardRemove())
    # Создание экземпляра класса PkpvdAuthorization
    pkpvd_author = PkpvdAuthorization()
    # Считать cookie с файла
    cookie_pkpvd = await pkpvd_author.read_cookie_from_file()
    # Проверка действительности cookie
    isCookieValid = await pkpvd_author.check_if_cookie_valid(cookie_pkpvd)
    # Если cookie не действителен
    if not isCookieValid:
        # Получить новый cookie
        cookie_pkpvd = await pkpvd_author.admin_authorization()
        # Сохранить cookie в файл
        await pkpvd_author.save_data_to_file(cookie_pkpvd)

    # Если авторизация в пк пвд провалилась
    if cookie_pkpvd == "":
        await message.answer("❗ Проблема с авторизацией в ПК ПВД. Обратитесь в IT-отдел", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот завершит состояние
        await state.finish()
        return
    # Если авторизация в пк пвд успешна
    # Получить номер обращения от пользователя
    number_of_req = message.text.upper()
    # Отправить запрос на сервер с номером обращения
    responseAppeal = requests.get(
        'http://10.42.200.207/api/rs/appeal/search2?page=0&size=5&sort=createDate,desc&startWith=false&internalNum='+number_of_req+'&packageNum'
        '=&statusNotePPOZ=&currentStep=&createDateFrom=&createDateTill=&createWho=&moveStepDate=&kudNum=&routineExecutionDays=&processingEndDateFrom='
        '&processingEndDateTill=&typeGosUslug=&cn=&textApplicants=',
        headers={'Cookie': 'JSESSIONID=' + cookie_pkpvd})
    # Получить json
    resp_json = responseAppeal.text
    # Прочитать json
    parsed_string = json.loads(resp_json)
    # Если content json пустой
    if len(parsed_string['content']) == 0:
        # Бот сообщит, что обращение не найдено
        await message.answer("Обращение не найдено.")
        # Создание клавиатуры для повтора
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('да', 'нет')
        # Бот предложить попробовать ещё раз найти обращение
        await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
        # Бот ожидает следующее состояниие с повтором попытки
        await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()
    # Если content json не пустой
    else:
        # Парсим id обращения
        id_appeal = parsed_string['content'][0]['id']
        print("JSON Appeal: ", parsed_string)
        # Отправляем запрос на сервер, чтобы получить Statement
        responseStatement = requests.get('http://10.42.200.207/api/rs/appeal/' + id_appeal + '/statement?page=0&size=5',
                                         headers={'Cookie': 'JSESSIONID=' + cookie_pkpvd})
        # Получаем json
        resp_json = responseStatement.text
        parsed_string = json.loads(resp_json)
        # Парсим id statement
        id_statement = parsed_string['content'][0]['id']
        print("JSON Statement: ", parsed_string)
        # Отправляем запрос, чтобы найти документ
        responseFindErrror = requests.get(
            'http://10.42.200.207/api/rs/appeal/' + id_appeal + '/' + id_statement + '/printstatement',
            headers={'Cookie': 'JSESSIONID=' + cookie_pkpvd})
        # Получаем текст ответа
        resp_document = responseFindErrror.text
        # parsed_string = json.loads(resp_json)
        # print("JSON print document: ", resp_document)
        # Булева переменная для определения, есть ли ошибка в заявлении или нет
        isDocError = True
        # Проверить заявление на ошибки, если json есть, значит есть ошибка, иначе нет ошибки
        try:
            json.loads(resp_document)
        except ValueError as err:
            isDocError = False

        print('Документ с ошибкой? ' + str(isDocError))
        # Перепенная в которой хранится состояние обращения
        documentCorrect = "С вашим обращением всё в порядке."
        # Если документ с ошибкой
        if isDocError:
            # Загрузить ответ json
            parsed_document_error = json.loads(resp_document)
            # Получить код ошибки
            code_error = parsed_document_error['status']
            # Получить сообщение ошибки
            message_error = parsed_document_error['message']
            # Переменная в которой указывается, что решение не найдено
            fix_not_found = 'Решение не найдено'
            # Получить список известных ошибок
            list_code_errors = list(available_pkpvd_errors.keys())
            # print(list_code_errors[0])
            solveError = 'Not solved'
            # Идем по списку ошибок
            for i in range(len(available_pkpvd_errors)):
                print('\n' + 'Ошибка: ' + list_code_errors[i])
                # Ищем ошибку сервера с известными ошибками
                index = message_error.find(list_code_errors[i])
                # Если не найдено
                if index == -1:
                    print('Not found')
                # Если найдено совпадение
                else:
                    print('Совпадение с ошибкой: ' + available_pkpvd_errors[list_code_errors[i]])
                    # Записываем решение в переменную
                    solveError = available_pkpvd_errors[list_code_errors[i]]
                    break
            # Если решение не найдено
            if solveError == 'Not solved':
                print('Решение не найдено...')
                # Бот сообщает, что решение не найдено
                await message.answer(fix_not_found)
                # Создаем кнопки для повтора
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.row('да', 'нет')
                # Бот предлагает попробовать ещё раз
                await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
                # Бот ожидает следующее состояние
                await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()
            # Если решение найдено
            else:
                print('Как решить: ' + solveError)
                # Бот сообщает, как решить проблему
                await message.answer(solveError)
                # Создание кнопок с повтором
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.row('да', 'нет')
                # Бот предлагает попробовать ещё раз
                await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
                # Бот ожидает состояние для повтора
                await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()
        # Если в документе нет ошибок
        else:
            # Бот сообщает, что с документом всё в порядке
            await message.answer(documentCorrect)
            # Создание кнопок для повтора
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('да', 'нет')
            # Бот предлагает попробовать ещё раз
            await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
            # Бот ожидает следующего состояния для повтора
            await OrderPkpvd.waiting_for_pkpvd_request_problem_try_again.set()

# Функция для повтора попытки найти обращение
async def pkpvd_request_problem_try_again(message: types.Message, state: FSMContext):
    # Если выбрано "да"
    if message.text.lower() == 'да':
        # Бот предлагает написать номер обращения
        await message.answer("⚠ Пожалуйста, напишите ваш номер обращения",
                             reply_markup=types.ReplyKeyboardRemove())
        # Бот ожидает состояния с поиском обращения
        await OrderPkpvd.waiting_for_pkpvd_request_problem.set()
    # Если выбрано "нет"
    elif message.text.lower() == 'нет':
        # Бот предлагает другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот завершает состояние
        await state.finish()
    # Иначе если выбран вариант не с кнопки
    else:
        # Бот предлагает вариант с кнопки
        await message.answer("⚠ Пожалуйста, выберите вариант из клавиатуры ниже\n"
                             "Побробовать ещё раз?")

# Регистрация хэндлеров для пк пвд
def register_handlers_pkpvd(dp: Dispatcher):
    # Хэндлер для команды с пк пвд
    dp.register_message_handler(pkpvd_start, commands="pkpvd", state="*")
    # Хэндлер для выбора проблемы с пк пвд
    dp.register_message_handler(pkpvd_problem_chosen, state=OrderPkpvd.waiting_for_pkpvd_problem)
    # Хэндлер для выбора проблемы с обращением
    dp.register_message_handler(pkpvd_request_problem, state=OrderPkpvd.waiting_for_pkpvd_request_problem)
    # Хэндлер для повторной попытки
    dp.register_message_handler(pkpvd_request_problem_try_again, state=OrderPkpvd.waiting_for_pkpvd_request_problem_try_again)
    # Хэндлер для выбора другой проблемы с пк пвд
    dp.register_message_handler(pkpvd_other_problem_chosen, content_types=types.ContentType.all(), state=OrderPkpvd.waiting_for_other_pkpvd_problem)
    # Поиск через регулярные выражения
    dp.register_message_handler(pkpvd_start, regexp=regexp_pkpvd, state="*")

