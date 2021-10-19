# Импорт библиотек для работы с сетью и json
import requests
import json
# Импорт библиотек для бота
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from fsm.app.admin_authorization.ais_authorization_admin import AisAuthorization
# Если запускать через консоль, то использовать строку ниже
# from app.admin_authorization.ais_authorization_admin import AisAuthorization
# Импорт конфигурационного файла
from fsm.app.config_reader import load_config
from aiogram.types import ParseMode
# Получение данных с конфигурационного файла
config = load_config("config/bot.ini")
# Получение id админ группы
admin_group_id = int(config.tg_bot.admin_group_id)

# Регулярные выражения для АИС
regexp_ais = '(\W|^)аис.*(\W|$)'
# Список проблем для АИС
available_ais_problems = ["проблема с АИС", "проблема с заявлением в АИС"]
# Словарь ошибок и решений к ошибкам
available_ais_errors = {
    'RejectionReasonCode: NO_DATA RejectionReasonDescription:': 'Вы загрузили файл слишком большого размера. Попробуйте загрузить файл меньшего размера.',
    'Question2': 'answer2',
    'Question3': 'answer3'
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
# Класс для АИС
class OrderAis(StatesGroup):
    waiting_for_ais_problem = State()
    waiting_for_other_ais_problem = State()
    waiting_for_ais_request_problem = State()
    waiting_for_ais_request_problem_try_again = State()

# Функция начала работы с АИС
async def ais_start(message: types.Message):
    # Создание кнопок для аис
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_ais_problems)
    # for name in available_ais_problems:
    #     keyboard.add(name)
    # Бот спрашивает пользователя
    await message.answer("🖥️ Какая у вас проблема с АИС? ", reply_markup=keyboard)
    # Бот ожидает следующее состояние выбор проблемы аис
    await OrderAis.waiting_for_ais_problem.set()

# Выбор проблемы с АИС
async def ais_problem_chosen(message: types.Message, state: FSMContext):
    # Если выбрана проблема не с кнопки
    if message.text not in available_ais_problems:
        # Бот сообщит пользователю
        await message.answer("⚠ Пожалуйста, выберите один из вариантов, используя клавиатуру ниже. ⚠")
        # Создать кнопки
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(*available_ais_problems)
        # Бот спросит проблему с АИС
        await message.answer("🖥️ Какая у вас проблема с АИС? ", reply_markup=keyboard)
        return
    # Если выбрана проблема с кнопки
    if message.text in available_ais_problems:
        # Если выбрано проблема с заявлением
        if message.text == available_ais_problems[len(available_ais_problems) - 1]:
            # Запись информации во временное хранилище
            await state.update_data(chosen_ais_request_problem=message.text.lower())
            # Бот спросит про номер заявления
            await message.answer("⚠ Пожалуйста, напишите ваш номер заявления \n❗ (ТОЛЬКО ЦИФРЫ)",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующее состояние
            await OrderAis.waiting_for_ais_request_problem.set()
        # Иначе, если выбрана проблема с аис
        else:
            # Бот спросит про вашу проблему с АИС
            await message.answer("⚠ Пожалуйста, напишите проблему, которая у вас случилась с АИС. Вы также можете прикрепить файл или фото с проблемой.",
                                 reply_markup=types.ReplyKeyboardRemove())
            # Бот ожидает следующее состояние с выбором проблемы с аис
            await OrderAis.waiting_for_other_ais_problem.set()

# Функция для выбора проблемы с аис
async def ais_other_problem_chosen(message: types.Message, state: FSMContext):
    # Если пользователь отправил боту документ
    if message.content_type == 'document':
        # Ответ в группу
        answer_to_group = f"🖥️ ⚠ Проблема с АИС..."
        # Бот сообщает, что выcлал в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предложит другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправит сообщение о проблеме в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот перешлет сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершит своё состояние
        await state.finish()
        # msg_document = message.document.file_id
        # print("msg doc "+msg_document)
        # await message.bot.send_document(admin_group_id, msg_document)
    # Если пользователь отправил боту фотографию
    elif message.content_type == 'photo':
        # Ответ в группу
        answer_to_group = f"🖥️ ⚠ Проблема с АИС..."
        # Бот сообщает, что выcлал в it-отдел
        await message.reply('Выслал IT-отделу', reply_markup=types.ReplyKeyboardRemove())
        # Бот предложит другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправит сообщение о проблеме в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот перешлет сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершит своё состояние
        await state.finish()
    # Если пользователь отправил боту текстовое сообщение
    elif message.content_type == 'text':
        print("test text")
        # Запись данных во временное хранилище
        await state.update_data(chosen_ais_problem=message.text.lower())
        # Считать данные со временного хранилища
        user_data = await state.get_data()
        # Текст для ответа
        answer_to_message = f"⚠ У вас текущая проблема с АИС: {user_data['chosen_ais_problem'].lower()} \n IT-специалист скоро свяжется с вами..."
        # Ответ в группу
        answer_to_group = f"🖥️ ⚠ Проблема с АИС: {user_data['chosen_ais_problem'].lower()}"
        # Бот ответит пользователю
        await message.reply(answer_to_message, reply_markup=types.ReplyKeyboardRemove())
        # Бот предложит другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот отправит сообщение о проблеме в группу
        await message.bot.send_message(admin_group_id, answer_to_group)
        # Бот перешлет сообщение от пользователя в группу
        await message.forward(admin_group_id)
        # Бот завершит своё состояние
        await state.finish()
    # return SendMessage(admin_group_id, answer_to_group)

# Функция для работы с номером заявления
async def ais_request_problem(message: types.Message, state: FSMContext):
    # Бот сообщает, что ищет решение проблемы
    await message.answer("⚠ ⏱️ Подождите, ищу решение проблемы...",
                         reply_markup=types.ReplyKeyboardRemove())
    # Создаем экземпляр класса AisAuthorization
    ais_author = AisAuthorization()
    # Считываем cookie с файла
    cookie_ais = await ais_author.read_cookie_from_file()
    # Проверяем действительность cookie
    isCookieValid = await ais_author.check_if_cookie_valid(cookie_ais)
    # Если cookie недействителен
    if not isCookieValid:
        # Получаем новое cookie
        cookie_ais = await ais_author.admin_authorization()
        # Сохраняем cookie в файл
        await ais_author.save_data_to_file(cookie_ais)

    # Если авторизация в аис провалилась
    if cookie_ais == "":
        await message.answer("❗ Проблема с авторизацией в АИС. Обратитесь в IT-отдел", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот завершит состояние
        await state.finish()
        return
    # Если авторизация в аис успешна
    # Номер заявления получаем от пользователя
    number_of_req = message.text
    # Payload для отправки в запрос
    payload = {"action": "orderService", "method": "getOrderHistory", "data": [number_of_req, False], "type": "rpc",
               "tid": 23}
    # Отправляем запрос на сервер
    response = requests.post(
        'http://192.168.99.91/cpgu/action/router',
        headers={'Cookie': 'JSESSIONID='+cookie_ais},
        json=payload)
    # Получаем json
    resp_json = response.text
    parsed_string = json.loads(resp_json)
    print("JSON: ", parsed_string)

    request_not_found = '⚠ Заявление не удалось найти. Проверьте номер заявления...'
    # получаем тип json
    json_type = parsed_string[0]['type']
    # Если тип json - rpc
    if json_type == 'rpc':
        # Заявление есть, ищем решение проблемы
        # Получаем список с историей заявления
        result = parsed_string[0]['result']
        # Размер списка
        result_size = len(result)
        # Сообщение об ошибке с сервера
        message_error = parsed_string[0]['result'][result_size - 1]['comment']
        # Сообщение если решение не удалось найти
        fix_not_found = 'К сожалению, решение не удалось найти. Попробуйте пересоздать заявление, правильно заполните все поля и попробуйте снова.\n' \
                        'Если ошибка не исчезнет, тогда позвоните в IT-отдел'
        # Получаем список ошибок со словаря
        list_code_errors = list(available_ais_errors.keys())
        # print(list_code_errors[0])
        solveError = 'Not solved'
        # Идём по словарю, если находим ошибку, то записываем решение
        for i in range(len(available_ais_errors)):
            print('\n' + 'Ошибка: ' + list_code_errors[i])
            index = message_error.find(list_code_errors[i])
            # Если не найдено
            if index == -1:
                print('Not found')
            # Если найдено совпадение
            else:
                print('Совпадение с ошибкой: ' + available_ais_errors[list_code_errors[i]])
                # Записываем решение в переменную
                solveError = available_ais_errors[list_code_errors[i]]
                break
        # Если решение не найдено
        if solveError == 'Not solved':
            print('Решение не найдено...')
            # Бот сообщит, что решение не найдено
            await message.answer(fix_not_found)
            # Создание кнопок для повтора попытки
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('да', 'нет')
            # Бот предлагает попробовать ещё раз найти заявление
            await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
            # Бот ожидает следующее состояние - повтор попытки
            await OrderAis.waiting_for_ais_request_problem_try_again.set()
        # Если решение найдено
        else:
            print('Как решить: ' + solveError)
            # Бот сообщает как решить проблему
            await message.answer(solveError)
            # Создание кнопок для повтора попытки
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('да', 'нет')
            # Бот предлагает попробовать ещё раз найти заявление
            await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
            # Бот ожидает следующее состояние - повтор попытки
            await OrderAis.waiting_for_ais_request_problem_try_again.set()
    # Если заявление не найдено
    elif json_type == 'exception':
        # Бот сообщает о том, что заявление не найдено
        await message.answer(request_not_found)
        # Создание кнопок для повтора попытки
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('да', 'нет')
        # Бот предлагает попробовать ещё раз найти заявление
        await message.answer("Побробовать ещё раз?", reply_markup=keyboard)
        # Бот ожидает следующее состояние - повтор попытки
        await OrderAis.waiting_for_ais_request_problem_try_again.set()


# Функция для повторной попытки найти заявления
async def ais_request_problem_try_again(message: types.Message, state: FSMContext):
    # Если выбрать "да"
    if message.text.lower() == 'да':
        # Бот предложит снова ввести номер заявления
        await message.answer("⚠ Пожалуйста, напишите ваш номер заявления \n❗ (ТОЛЬКО ЦИФРЫ)",
                             reply_markup=types.ReplyKeyboardRemove())
        # Бот ожидает состояние в поиске заявления
        await OrderAis.waiting_for_ais_request_problem.set()
    # Если выбрать "нет"
    elif message.text.lower() == 'нет':
        # Бот предложит другие функции
        await message.answer(other_functions, reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        # Бот завершит состояние
        await state.finish()
    else:
        # Если выбран вариант не с кнопки
        await message.answer("⚠ Пожалуйста, выберите вариант из клавиатуры ниже\n"
                             "Побробовать ещё раз?")

# Регистрация хэндлеров (перехватывают сообщения)
def register_handlers_ais(dp: Dispatcher):
    # Хэндлер, если пользователь выбрал команду для аис
    dp.register_message_handler(ais_start, commands="ais", state="*")
    # Хэндлер для выбора проблемы с аис
    dp.register_message_handler(ais_problem_chosen, state=OrderAis.waiting_for_ais_problem)
    # Хэндлер для выбора проблемы с заявлением
    dp.register_message_handler(ais_request_problem, state=OrderAis.waiting_for_ais_request_problem)
    # Хэндлер для повторной попытки с заявлением
    dp.register_message_handler(ais_request_problem_try_again, state=OrderAis.waiting_for_ais_request_problem_try_again)
    # Хэндлер для других проблем
    dp.register_message_handler(ais_other_problem_chosen, content_types=types.ContentType.all(), state=OrderAis.waiting_for_other_ais_problem)
    # Поиск через регулярные выражения
    dp.register_message_handler(ais_start, regexp=regexp_ais, state="*")
