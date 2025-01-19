from aiogram.types import Message, CallbackQuery
from typing import Callable, Awaitable, Dict, Any
from aiogram import  BaseMiddleware
from cachetools import TTLCache

class AnitFloodMiddleware(BaseMiddleware):
    #Создаем Кеш с максимальным количеством элементов 10_000
    #и устанавливаем время хранения данных(ttl)
    def __init__(self, limit: int=2) -> None:
        self.limit = TTLCache(maxsize=10000, ttl=limit)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        #Проверяем если ли id пользователя в хранилище
        #если есть то игнорируем апдейт
        if event.from_user.id in self.limit:
            return
        #ID нет, заносим его в хранилище
        else:
            self.limit[event.from_user.id] = None
        return await handler(event, data)
