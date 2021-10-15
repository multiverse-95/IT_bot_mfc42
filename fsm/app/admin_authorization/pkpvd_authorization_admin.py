import requests
import json

from fsm.app.config_reader import load_config
# Класс для авторизации в пк пвд
class PkpvdAuthorization:
    # Функция для авторизации как администратор
    async def admin_authorization(self):
        # Парсинг файла конфигурации
        config = load_config("config/bot.ini")
        # Получаем логин с конфиг файла
        login = config.tg_bot.admin_pkpvd_login
        # Получаем пароль с конфиг файла
        password = config.tg_bot.admin_pkpvd_password
        # создаём сессию
        session = requests.session()
        # Url к которому будет отправлен запрос
        url = "http://10.42.200.207/api/rs/login?returi=http%3A%2F%2F10.42.200.207%2Fhelp"
        # Параметры запроса
        params = {'redirect': 'http://10.42.200.207/help', 'username': login, 'password': password, 'commit': 'Войти'}
        # Отправляем post-запрос с параметрами
        response = session.post(url, data=params)
        print("Status autor pkPVD:", response.status_code)
        # Получаем cookie
        cookie_pkpvd = str(session.cookies.get("JSESSIONID"))
        print("cookie:", cookie_pkpvd)
        # Возвращаем cookie
        return cookie_pkpvd

    # Функция для сохранения cookie в файл
    async def save_data_to_file(self, cookiePkpvd):
        # Парсинг файла конфигурации
        config = load_config("config/bot.ini")
        # Получаем логин с конфиг файла
        loginPkpvd = config.tg_bot.admin_pkpvd_login
        # Получаем пароль с конфиг файла
        passwordPkPvd = config.tg_bot.admin_pkpvd_password
        # Сохраняем логин, пароль и cookie в файл
        dataPkpvd = {'login_pkpvd': loginPkpvd, 'password_pkpvd': passwordPkPvd, 'cookie_pkpvd': cookiePkpvd}

        with open(r"C:\it_bot_mfc42\it_bot_pkpvd_settings.json", 'w', encoding='utf-8') as f:
            json.dump(dataPkpvd, f, ensure_ascii=False, indent=4)

    # Функция для чтения cookie с файла
    async def read_cookie_from_file(self):
        # Откроем файл с настройками
        with open(r"C:\it_bot_mfc42\it_bot_pkpvd_settings.json", encoding='utf-8') as f:
            data_from_json = json.load(f)

        print(data_from_json)
        # Парсим cookie
        cookie_from_json = data_from_json['cookie_pkpvd']
        print('cookie json file', data_from_json['cookie_pkpvd'])
        # Возвращаем cookie
        return cookie_from_json

    # Функция для проверки корректности cookie
    async def check_if_cookie_valid(self, cookie):
        # Создаём сессию
        session = requests.session()
        # Url на который будет отправлен запрос, для проверки cookie
        getUrlPkpvd = "http://10.42.200.207/api/rs/reports/list"
        # Отправляем get-запрос
        response = session.get(getUrlPkpvd, headers={'Cookie': 'JSESSIONID=' + cookie})  # получаем cookie
        print("Status checkCookie:", response.status_code)
        # Получаем статус код
        status_code = response.status_code
        # Проверяем статус код
        isCookievalid = validateResult(status_code)
        # Возвращаем результат корректности cookie
        return isCookievalid

# Проверка cookie на корректность
def validateResult(status_code):
    # Если результат с сервера 200, то cookie действителен, иначе нет
    if status_code == 200:
        print("cookie pk pvd correct!")
        return True
    else:
        print("cookie pk pvd NOT correct!")
        return False
