from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import TradeState
from db import get_balances, update_balance

# /play հրաման
async def play_handler(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="🧪 Դեմո", callback_data="mode_demo")
    builder.button(text="💰 Իրական", callback_data="mode_real")
    builder.adjust(2)

    await message.answer("Ընտրեք խաղի ռեժիմը՝", reply_markup=builder.as_markup())
    await state.set_state(TradeState.choosing_mode)

# Ընտրում է ռեժիմ
async def mode_chosen(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data.split("_")[1]
    await state.update_data(mode=mode)
    await callback.message.answer("Մուտքագրեք գումարը՝ $")
    await state.set_state(TradeState.entering_amount)
    await callback.answer()

# Մուտքագրում է գումար
async def amount_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mode = data['mode']
    user_id = message.from_user.id
    try:
        amount = float(message.text)
        demo, real = await get_balances(user_id)
        balance = demo if mode == "demo" else real
        if amount <= 0 or amount > balance:
            return await message.answer("Գումարը սխալ է կամ գերազանցում է մնացորդը։")
        await state.update_data(amount=amount)
        
        builder = InlineKeyboardBuilder()
        builder.button(text="BUY 📈", callback_data="do_buy")
        builder.button(text="SELL 📉", callback_data="do_sell")
        builder.adjust(2)
        await message.answer("Ընտրեք գործողությունը՝", reply_markup=builder.as_markup())
        await state.set_state(TradeState.confirming_action)

    except ValueError:
        await message.answer("Խնդրում եմ մուտքագրեք ճիշտ թիվ։")

# BUY կամ SELL գործողություն
async def action_chosen(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    action = callback.data.split("_")[1]  # buy կամ sell
    amount = data['amount']
    mode = data['mode']
    user_id = callback.from_user.id

    demo, real = await get_balances(user_id)
    balance_type = 'demo' if mode == 'demo' else 'real'

    # Շահույթ կամ կորուստ
    import random
    percent_change = random.uniform(-0.4, 1.0)
    result = round(amount + (amount * percent_change), 2)
    profit = result - amount

    await update_balance(user_id, -amount, balance_type=balance_type)
    await update_balance(user_id, result, balance_type=balance_type)

    new_balance = demo - amount + result if mode == 'demo' else real - amount + result

    text = f"🎮 Խաղի ռեժիմ՝ {'Դեմո' if mode == 'demo' else 'Իրական'}\n" \
           f"Գործողություն՝ {action.upper()}\n" \
           f"Մուտքագրած գումար՝ ${amount:.2f}\n" \
           f"{'📈 Շահույթ' if profit > 0 else '📉 Կորուստ'}՝ {profit:.2f}$\n" \
           f"💼 Նոր մնացորդ՝ ${new_balance:.2f}"

    await callback.message.answer(text)
    await state.clear()
    await callback.answer()
