from aiogram.fsm.state import StatesGroup, State

class Context(StatesGroup):
  WAIT_PROFFESION = State()
  DATA_VAC = State()
  