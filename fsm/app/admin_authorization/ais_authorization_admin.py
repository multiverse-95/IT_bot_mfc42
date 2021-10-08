import requests
import json

from fsm.app.config_reader import load_config

class AisAuthorization:
    async def admin_authorization(self):
        # Парсинг файла конфигурации
        config = load_config("config/bot.ini")
        login = config.tg_bot.admin_ais_login
        password = config.tg_bot.admin_ais_password
        session = requests.session()  # создаём сессию
        url = "http://192.168.99.91/cpgu/action/user/login"
        session.get(url)  # получаем cookie
        payload = {"username": login, "password": password}
        response = session.post(url, json=payload)  # логинимся
        print("Status autor 1:", response.status_code)
        first_cookie = str(session.cookies.get("JSESSIONID"))
        print("First cookie:", first_cookie)

        # Second autor
        print("Confirm autoriz")
        session = requests.session()  # создаём сессию
        url = "http://192.168.99.91/cpgu/action/user/login"
        session.get(url)  # получаем cookie
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

        # Get Admin Role
        print("Admin role")
        session = requests.session()  # создаём сессию
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)  # получаем cookie
        payload = {"action": "authController", "method": "getCurrentUser", "data": [], "type": "rpc", "tid": 1}
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

        print("Admin role")
        session = requests.session()  # создаём сессию
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)  # получаем cookie
        payload = {"action": "changeWorkingAttributesService", "method": "setWorkingMfcId", "data": [35149, "LOGIN"],
                   "type": "rpc", "tid": 2}
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

        print("Admin role")
        session = requests.session()  # создаём сессию
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)  # получаем cookie
        payload = {"action": "authController", "method": "singleAuthorityLogin", "data": ["ROLE_ADMIN", False],
                   "type": "rpc", "tid": 3}
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

        print("Admin role")
        session = requests.session()  # создаём сессию
        url = "http://192.168.99.91/cpgu/action/router"
        session.get(url)  # получаем cookie
        payload = {"action": "cpguConfigurationService", "method": "getConfiguration", "type": "rpc", "tid": 4}
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

        return first_cookie

    async def save_data_to_file(self, cookieAis):
        config = load_config("config/bot.ini")
        loginAis = config.tg_bot.admin_ais_login
        passwordAis = config.tg_bot.admin_ais_password
        dataAis = {'login_ais': loginAis, 'password_ais': passwordAis, 'cookie_ais': cookieAis}
        with open(r"C:\it_bot_mfc42\it_bot_ais_settings.json", 'w', encoding='utf-8') as f:
            json.dump(dataAis, f, ensure_ascii=False, indent=4)

    async def read_cookie_from_file(self):
        with open(r"C:\it_bot_mfc42\it_bot_ais_settings.json", encoding='utf-8') as f:
            data_from_json = json.load(f)

        print(data_from_json)
        cookie_from_json = data_from_json['cookie_ais']
        print('cookie json file', data_from_json['cookie_ais'])
        return cookie_from_json

    async def check_if_cookie_valid(self, cookie):

        session = requests.session()  # создаём сессию
        getUrlAis = "http://192.168.99.91/cpgu/action/getMfcs?_dc=1631065722349&showClosed=true&page=1&start=0&limit=500&sort=%5B%7B%22property%22%3A%22code%22%2C%22direction%22%3A%22ASC%22%7D%5D"
        response = session.get(getUrlAis, headers={'Cookie': 'JSESSIONID=' + cookie})  # получаем cookie
        print("Status checkCookie 2:", response.status_code)
        # print(len(session.cookies.items()))

        if response.status_code == 200:
            print("Login Success!")
        else:
            print("Login FAILED!")

        resp_json = response.text
        # parsed_string = json.loads(resp_json)
        print("JSON VALID "+ str(validateJSON(resp_json)))
        isJsonValid = validateJSON(resp_json)
        return isJsonValid


def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True
