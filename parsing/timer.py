import asyncio

from parsing import parser
from logs.logger import get_logger

class ParserApp:
    hours : int = 24
    started : bool = True
    logger = get_logger(name=__name__)

    async def timer(self):

        while self.started:
            self.logger.info("Running func timer()")
            await parser.point_run()
            self.logger.info(f"Waiting {self.hours}h")
            await asyncio.sleep(self.hours*3600)

        while not self.started:
            await asyncio.sleep(900)

    async def change_time(self, hour: int):
        self.logger.info(f"Waiting time changed from {self.hours} to {hour}")
        self.hours = hour

    async def start_off(self, value: bool):
        self.logger.info(f"Active mode changed from {self.started} to {value}")
        self.started = value

    async def show(self):
        print(self.hours)
        print(self.started)