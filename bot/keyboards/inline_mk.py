from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.callback_factory import CallbackCity, CallbackVac


async def inline_menu(city_have: bool):
  if city_have:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Change city", callback_data="change"))

    return builder.as_markup(resize_keyboard=True)

  else:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Chose city", callback_data="chose"))

    return builder.as_markup(resize_keyboard=True)
  
async def city_level_0():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Астана", callback_data=CallbackCity(action="Астана").pack()),
        InlineKeyboardButton(text="Алмата", callback_data=CallbackCity(action="Алмата").pack()),
        InlineKeyboardButton(text="Акмола", callback_data=CallbackCity(action="Акмола").pack()),
        InlineKeyboardButton(text="Актобе", callback_data=CallbackCity(action="Актобе").pack()),
        InlineKeyboardButton(text="Атырау", callback_data=CallbackCity(action="Атырау").pack()),
        InlineKeyboardButton(text="Абай", callback_data=CallbackCity(action="Абай").pack()),
        InlineKeyboardButton(text="Алматинский регион", callback_data=CallbackCity(action="Алматинский регион").pack()),
        InlineKeyboardButton(text="Восточный регион", callback_data=CallbackCity(action="Восточный регион").pack()),
        InlineKeyboardButton(text="Жамбыл", callback_data=CallbackCity(action="Жамбыл").pack()),
        InlineKeyboardButton(text="Жетысу", callback_data=CallbackCity(action="Жетысу").pack()),
        InlineKeyboardButton(text="Далее", callback_data=CallbackCity(action="Далее", page=0).pack())
    )
    builder.adjust(2)

    return builder.as_markup()

async def city_level_1():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Западный регион", callback_data=CallbackCity(action="Западный регион").pack()),
        InlineKeyboardButton(text="Караганда", callback_data=CallbackCity(action="Караганда").pack()),
        InlineKeyboardButton(text="Костанай", callback_data=CallbackCity(action="Костанай").pack()),
        InlineKeyboardButton(text="Кызылорда", callback_data=CallbackCity(action="Кызылорда").pack()),
        InlineKeyboardButton(text="Мангыстау", callback_data=CallbackCity(action="Мангыстау").pack()),
        InlineKeyboardButton(text="Павлодар", callback_data=CallbackCity(action="Павлодар").pack()),
        InlineKeyboardButton(text="Туркестан", callback_data=CallbackCity(action="Туркестан").pack()),
        InlineKeyboardButton(text="Северный регион", callback_data=CallbackCity(action="Северный регион").pack()),
        InlineKeyboardButton(text="Улытау", callback_data=CallbackCity(action="Улытау").pack()),
        InlineKeyboardButton(text="Шимкент", callback_data=CallbackCity(action="Шимкент").pack()),
        InlineKeyboardButton(text="Назад", callback_data=CallbackCity(action="Назад", page=1).pack())
    )
    builder.adjust(2)

    return builder.as_markup()

async def navigation_vac(page: int=0):

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="back", callback_data=CallbackVac(action="prev",page=page).pack()),
        InlineKeyboardButton(text="menu", callback_data=CallbackVac(action="menu",page=page).pack()),
        InlineKeyboardButton(text="next", callback_data=CallbackVac(action="next",page=page).pack())
    )

    return builder.as_markup()
