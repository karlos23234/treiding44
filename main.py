from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers import play_handler, mode_chosen, amount_entered, action_chosen
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())

dp.message.register(play_handler, Command("play"))
dp.callback_query.register(mode_chosen, F.data.startswith("mode_"), state=TradeState.choosing_mode)
dp.message.register(amount_entered, state=TradeState.entering_amount)
dp.callback_query.register(action_chosen, F.data.startswith("do_"), state=TradeState.confirming_action)

