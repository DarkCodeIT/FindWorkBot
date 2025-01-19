from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import db_service
from bot.keyboards.inline_mk import navigation_vac
from bot.utils.formating import formating
from bot.utils.fsm import Context
from const import rus_city_id

router_message = Router(name="Message_router")

@router_message.message(F.text == "Search")
async def search(msg: Message, state: FSMContext):
    #Получение данных о пользователе
    user_id_tg = msg.from_user.id
    response = await db_service.get_user(user_id=user_id_tg)

    #Проверка выбран ли город у пользователя
    if "city" in response:
        #Ожидаем профессию от пользователя
        await state.set_state(Context.WAIT_PROFFESION)
        await msg.answer(text="Теперь введите профессию")

    else:
        await msg.answer(text="Упс.. похоже вы не выбрали ваш город(")


@router_message.message(F.text == "Information")
async def information_about_user(message: Message, state: FSMContext):
    await state.clear()
    response = await db_service.get_user(user_id=message.from_user.id)

    if "city" in response:
        await message.answer(text=f"Ваш ID: {message.from_user.id}\nВаш город: {response["city"]}")

    else:
        await message.answer(text=f"Ваш ID: {message.from_user.id}\nВаш город: Не выбран")


@router_message.message(F.text, Context.WAIT_PROFFESION)
async def profession_msg(msg: Message, state: FSMContext):
    await state.clear()

    #Получаем ID города который выбран у пользователя
    response = await db_service.get_user(user_id=msg.from_user.id)
    city_id = rus_city_id[response["city"]]

    #Получаем вакансии
    data = await db_service.get_vacansy(city_id=city_id, prof=msg.text)

    #Структурируем данные
    lst_of_vac = await formating(data)

    #Используем FSMContext как временное хранилище
    await state.update_data(data={"DATA_VAC" : lst_of_vac})
    await msg.answer(text=lst_of_vac[0], reply_markup= await navigation_vac(page=0))