import aiogram

from aiogram.filters import CommandStart
from aiogram.types.message import Message
from aiogram.fsm.context import FSMContext

from database import db_service
from bot.keyboards.inline_mk import inline_menu

router_command = aiogram.Router(name="Command_router")

@router_command.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    #Удаление всех состояний, чтобы не возникало ошибок
    await state.clear()

    #Проверка есть ли пользователь в БД
    user_tg_id = msg.from_user.id
    response = await db_service.get_user(user_id=user_tg_id)

    #Если нет, загружаем данные о пользователе
    if not response:
        user_data = dict(
            user_tg_id=user_tg_id,
            first_name=msg.from_user.first_name,
            last_name=msg.from_user.last_name,
            username=msg.from_user.username,
            premium=msg.from_user.is_premium
        )

        await db_service.insert(data=user_data, coll="user")
        await msg.answer(text="О вы у нас новенький, приветсвтую!", reply_markup=await inline_menu(city_have=False))

    else:
        if "city" in response:
            await msg.answer(text="О это снова вы.", reply_markup=await inline_menu(city_have=True))
        else:
            await msg.answer(text="О это снова вы.", reply_markup=await inline_menu(city_have=False))