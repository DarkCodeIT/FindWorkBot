from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

async def menu_r():
  builder = ReplyKeyboardBuilder()
  builder.add(KeyboardButton(text="Search"))
  builder.add(KeyboardButton(text="Information"))
  return builder.as_markup(resize_keyboard=True)

async def admin_panel():
  builder = ReplyKeyboardBuilder()
  builder.row(KeyboardButton(text="Статистика"))
  return builder.as_markup(resize_keyboard=True)
  