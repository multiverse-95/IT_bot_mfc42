import requests
import json

from fsm.app.config_reader import load_config
# Класс, отвечающий за авторизацию в АИС
class AisAuthorization:
    async def admin_authorization(self):
        # Парсинг файла конфигурации
        config = load_config("config/bot.ini")
        # Получаем логин с конфиг файла
        login = config.tg_bot.admin_ais_login
        # Получаем пароль с конфиг файла
        password = config.tg_bot.admin_ais_password
        # Создаём сессию
        session = requests.session()
        # url адрес на который будет отправлен запрос
        url = "http://192.168.99.91/cpgu/action/user/login"
        # Получаем cookie
        session.get(url)
        # payload для запроса
        payload = {"username": login, "password": password}
        # Отправляем post запрос
        response = session.post(url, json=payload)
        print("Status autor 1:", response.status_code)
        # Получаем cookie, который позже активируем
        first_cookie = str(session.cookies.get("JSESSIONID"))
        print("First cookie:", first_cookie)

        # Второй этап авторизации
        print("Confirm autoriz")
        # Создаём сессию
        session = requests.session()
        # url адрес на который будет отправлен запрос
        url = "http://192.168.99.91/cpgu/action/user/login"
        # получаем cookie
        session.get(url)
        # Отправляем post запрос, с cookie в header
        response = session.post(
            'http://192.168.99.91/cpgu/action/user/login',
            headers={'Cookie': 'JSESSIONID=' + first_cookie},
            json=payload)
        print("Status autor 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")

        # Получение прав администратора в АИС
        print("Admin role")
        # создаём сессию
        session = requests.session()
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)
        # payload
        payload = {"action": "authController", "method": "getCurrentUser", "data": [], "type": "rpc", "tid": 1}
        # Отправляем post запрос
        response = session.post(
            url,
            headers={'Cookie': 'JSESSIONID=' + first_cookie},
            json=payload)
        print("Status autor 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")


        # Второй этап для получения прав администратора в АИС
        print("Admin role")
        # создаём сессию
        session = requests.session()
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)  # получаем cookie
        payload = {"action": "changeWorkingAttributesService", "method": "setWorkingMfcId", "data": [35149, "LOGIN"],
                   "type": "rpc", "tid": 2}
        # Отправляем запрос
        response = session.post(
            url,
            headers={'Cookie': 'JSESSIONID=' + first_cookie},
            json=payload)
        print("Status autor 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")

        # Третий этап для получения прав администратора в АИС
        print("Admin role")
        session = requests.session()
        # создаём сессию
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)
        payload = {"action": "authController", "method": "singleAuthorityLogin", "data": ["ROLE_ADMIN", False],
                   "type": "rpc", "tid": 3}
        # Отправляем запрос
        response = session.post(
            url,
            headers={'Cookie': 'JSESSIONID=' + first_cookie},
            json=payload)
        print("Status autor 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")
        # Четвертый этап для получения прав администратора в АИС
        print("Admin role")
        # создаём сессию
        session = requests.session()
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)
        payload = {"action": "cpguConfigurationService", "method": "getConfiguration", "type": "rpc", "tid": 4}
        # Отправляем запрос
        response = session.post(
            url,
            headers={'Cookie': 'JSESSIONID=' + first_cookie},
            json=payload)
        print("Status autor 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")
        # Возвращаем итоговый cookies
        return first_cookie

    # Функция для сохранения cookie в файл
    async def save_data_to_file(self, cookieAis):
        # Получение данных с конфигурационного файла
        config = load_config("config/bot.ini")
        # Получаем логин с конфиг файла
        loginAis = config.tg_bot.admin_ais_login
        # Получаем пароль с конфиг файла
        passwordAis = config.tg_bot.admin_ais_password
        dataAis = {'login_ais': loginAis, 'password_ais': passwordAis, 'cookie_ais': cookieAis}
        with open(r"C:\it_bot_mfc42\it_bot_ais_settings.json", 'w', encoding='utf-8') as f:
            json.dump(dataAis, f, ensure_ascii=False, indent=4)

    # Функция для чтения cookie с конфиг файла
    async def read_cookie_from_file(self):
        with open(r"C:\it_bot_mfc42\it_bot_ais_settings.json", encoding='utf-8') as f:
            data_from_json = json.load(f)

        print(data_from_json)
        # Парсим cookie с файла
        cookie_from_json = data_from_json['cookie_ais']
        print('cookie json file', data_from_json['cookie_ais'])
        # Возвращаем cookie
        return cookie_from_json

    # Функция для проверки действительности cookie
    async def check_if_cookie_valid(self, cookie):
        # создаём сессию
        session = requests.session()
        # Url адрес к которому будет отправлен запрос для проверки cookie
        getUrlAis = "http://192.168.99.91/cpgu/action/getMfcs?_dc=1631065722349&showClosed=true&page=1&start=0&limit=500&sort=%5B%7B%22property%22%3A%22code%22%2C%22direction%22%3A%22ASC%22%7D%5D"
        # Отправляем get-запрос с cookie
        response = session.get(getUrlAis, headers={'Cookie': 'JSESSIONID=' + cookie})
        print("Status checkCookie 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")
        # Получаем ответ с сервера
        resp_json = response.text
        # parsed_string = json.loads(resp_json)
        print("JSON VALID "+ str(validateJSON(resp_json)))
        # Проверяем json на корректность
        isJsonValid = validateJSON(resp_json)
        # Возвращаем результат проверки
        return isJsonValid

# Функция для проверки json на корректность
def validateJSON(jsonData):
    # Если json корректный, возвращаем true, иначе false
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True
