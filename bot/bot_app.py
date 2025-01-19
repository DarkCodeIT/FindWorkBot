import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers.command import router_command
from bot.handlers.callback import router_callback
from bot.handlers.message import router_message
from bot.handlers.admin import router_admin

from bot.middlewares.antiflood import AnitFloodMiddleware

async def start_bot():
    load_dotenv()

    dp = Dispatcher()
    bot = Bot(os.getenv("TOKEN"))
    #Подключаем Midlleware к диспетчеру, чтобы они работали на всех роутерах
    dp.message.middleware(AnitFloodMiddleware())
    dp.callback_query.middleware(AnitFloodMiddleware())

    dp.include_routers(
        router_command,
        router_callback,
        router_message,
        router_admin
    )

    try:
        await dp.start_polling(bot)
        return bot

    except Exception as ex:
        return ex