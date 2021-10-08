import requests
import json

from fsm.app.config_reader import load_config

class PkpvdAuthorization:
    async def admin_authorization(self):
        # Парсинг файла конфигурации
        config = load_config("config/bot.ini")
        login = config.tg_bot.admin_pkpvd_login
        password = config.tg_bot.admin_pkpvd_password
        session = requests.session()  # создаём сессию
        url = "http://10.42.200.207/api/rs/login?returi=http%3A%2F%2F10.42.200.207%2Fhelp"
        params = {'redirect': 'http://10.42.200.207/help', 'username': login, 'password': password, 'commit': 'Войти'}
        response = session.post(url, data=params)  # логинимся
        print("Status autor pkPVD:", response.status_code)
        cookie_pkpvd = str(session.cookies.get("JSESSIONID"))
        print("cookie:", cookie_pkpvd)

        return cookie_pkpvd

    async def save_data_to_file(self, cookiePkpvd):
        config = load_config("config/bot.ini")
        loginPkpvd = config.tg_bot.admin_pkpvd_login
        passwordPkPvd = config.tg_bot.admin_pkpvd_password
        dataPkpvd = {'login_pkpvd': loginPkpvd, 'password_pkpvd': passwordPkPvd, 'cookie_pkpvd': cookiePkpvd}
        with open(r"C:\it_bot_mfc42\it_bot_pkpvd_settings.json", 'w', encoding='utf-8') as f:
            json.dump(dataPkpvd, f, ensure_ascii=False, indent=4)

    async def read_cookie_from_file(self):
        with open(r"C:\it_bot_mfc42\it_bot_pkpvd_settings.json", encoding='utf-8') as f:
            data_from_json = json.load(f)

        print(data_from_json)
        cookie_from_json = data_from_json['cookie_pkpvd']
        print('cookie json file', data_from_json['cookie_pkpvd'])
        return cookie_from_json

    async def check_if_cookie_valid(self, cookie):

        session = requests.session()  # создаём сессию
        getUrlPkpvd = "http://10.42.200.207/api/rs/reports/list"
        response = session.get(getUrlPkpvd, headers={'Cookie': 'JSESSIONID=' + cookie})  # получаем cookie
        print("Status checkCookie:", response.status_code)
        status_code = response.status_code
        isCookievalid=validateResult(status_code)

        return isCookievalid


def validateResult(status_code):
    if status_code == 200:
        print("cookie pk pvd correct!")
        return True
    else:
        print("cookie pk pvd NOT correct!")
        return False
