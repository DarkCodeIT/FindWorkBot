import asyncio

from bot import bot_app
from parsing.timer import ParserApp
from logs.logger import get_logger

async def main():
    logger = get_logger(name=__name__)

    try:
        logger.info("Running bot")
        # Запускаем задачу бота асинхронно
        bot_task = asyncio.create_task(bot_app.start_bot())

        logger.info("Running parsing")
        # Создаем задачу для парсера
        mytimer = ParserApp()
        parser_task = asyncio.create_task(mytimer.timer())

        # Ждем завершения всех задач
        await bot_task
        await parser_task

        logger.info("Bot and Parser are done")

    except Exception as ex:
        logger.error("Error in module run.py:")
        logger.error(f"{ex}")

if __name__ == "__main__":
    asyncio.run(main())