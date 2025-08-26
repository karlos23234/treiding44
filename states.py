from aiogram.fsm.state import State, StatesGroup

class TradeState(StatesGroup):
    choosing_mode = State()
    entering_amount = State()
    confirming_action = State()
