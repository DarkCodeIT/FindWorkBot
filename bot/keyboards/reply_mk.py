from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

async def menu_r():
  builder = ReplyKeyboardBuilder()
  builder.row(KeyboardButton(text="Поиск🔎"), KeyboardButton(text="Мои данные📋"))
  builder.row(KeyboardButton(text="Изменить город🌆"))
  return builder.as_markup(resize_keyboard=True)

async def admin_panel():
  builder = ReplyKeyboardBuilder()
  builder.row(KeyboardButton(text="Статистика"))
  return builder.as_markup(resize_keyboard=True)
  