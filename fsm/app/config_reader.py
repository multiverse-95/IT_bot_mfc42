import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    admin_ais_login: str
    admin_ais_password: str
    admin_pkpvd_login: str
    admin_pkpvd_password: str
    admin_group_id: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            admin_ais_login=tg_bot["admin_ais_login"],
            admin_ais_password=tg_bot["admin_ais_password"],
            admin_pkpvd_login=tg_bot["admin_pkpvd_login"],
            admin_pkpvd_password=tg_bot["admin_pkpvd_password"],
            admin_group_id=tg_bot["admin_group_id"]
        )
    )
