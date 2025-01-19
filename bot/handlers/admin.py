from aiogram.filters.command import Command
from aiogram import types, F, Router

from bot.keyboards.reply_mk import admin_panel
from database import statistic

router_admin = Router(name="admin")

@router_admin.message(Command(commands=["panel"]))
async def start_admin_panel(msg: types.Message):
    if msg.from_user.id == 7487991103:
        id_user = msg.message_id
        await msg.answer(text="Привет, Админ!", reply_markup= await admin_panel())
        await msg.delete(message_id=id_user)

@router_admin.message(F.text == "Статистика")
async def show_statistic(msg: types.Message):
    if msg.from_user.id == 7487991103:
        count_users = await statistic.get_count_of_users()
        count_clicks_to_citys = await statistic.get_count_cliks_to_city()

        await msg.answer(text=count_users)
        await msg.answer(text=count_clicks_to_citys)