from aiogram.filters.callback_data import CallbackData

class CallbackCity(CallbackData, prefix="callback_city"):
  action: str
  page: int = 0

class CallbackVac(CallbackData, prefix="callback_vac"):
  action: str
  page: int = 0