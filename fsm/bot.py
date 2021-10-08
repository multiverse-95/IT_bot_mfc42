import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import load_config
from app.handlers.ais import register_handlers_ais
from app.handlers.pkpvd import register_handlers_pkpvd
from app.handlers.buh1C import register_handlers_buh_1C
from app.handlers.queue_mfc import register_handlers_queue
from app.handlers.printer import register_handlers_printer
from app.handlers.common import register_handlers_common

logger = logging.getLogger(__name__)


# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="🔑 Начало работы бота"),
        BotCommand(command="/help", description="❓ Помощь по боту"),
        BotCommand(command="/ais", description="🖥️ Вопросы по АИС"),
        BotCommand(command="/pkpvd", description="📋 Вопросы по ПК ПВД"),
        BotCommand(command="/1c", description="📚 Вопросы по 1C"),
        BotCommand(command="/queue", description="⏳ Вопросы по очереди"),
        BotCommand(command="/printer", description="🖨️ Вопросы по принтеру"),
        BotCommand(command="/cancel", description="🚫 Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Парсинг файла конфигурации
    config = load_config("config/bot.ini")

    # Объект бота
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_ais(dp)
    register_handlers_pkpvd(dp)
    register_handlers_buh_1C(dp)
    register_handlers_queue(dp)
    register_handlers_printer(dp)


    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.start_polling()


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot is finished!")
