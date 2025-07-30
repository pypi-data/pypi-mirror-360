from asyncio import create_task
from datetime import timedelta, datetime

import PGram
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from xync_schema import models
from aiogram.utils.keyboard import InlineKeyboardBuilder
from xync_bot.routers.pay import cd, dep, window

pay = Router()


@pay.message(Command("pay"))
async def h_start(msg: Message):
    """Step 1: Select target type"""
    msg.bot.store.curr.is_target = True
    await msg.delete()
    await window.type_select(msg)


@pay.callback_query(cd.TargetType.filter(F.is_fiat))
async def h_got_fiat_type(query: CallbackQuery, bot: PGram):
    """Step 2f: Select cur"""
    await query.answer("Понял, фиат")
    bot.store.curr.is_fiat = True
    await window.cur_select(query.message)


@pay.callback_query(cd.TargetType.filter(F.is_fiat.__eq__(0)))
async def h_got_crypto_type(query: CallbackQuery, bot: PGram):
    """Step 2c: Select coin"""
    bot.store.curr.is_fiat = False
    await query.answer("Понял, крипта")
    await window.coin_select(query.message)


@pay.callback_query(cd.Coin.filter())
async def h_got_coin(query: CallbackQuery, callback_data: cd.Coin, bot: PGram):
    """Step 3c: Select target ex"""
    setattr(bot.store.curr, ("t" if bot.store.curr.is_target else "s") + "_coin_id", callback_data.id)
    await query.answer("Эта монета есть на следующих биржах")
    await window.ex_select(query.message)


@pay.callback_query(cd.Cur.filter())
async def h_got_cur(query: CallbackQuery, callback_data: cd.Cur, bot: PGram):
    """Step 3f: Select target pm"""
    setattr(bot.store.curr, ("t" if bot.store.curr.is_target else "s") + "_cur_id", callback_data.id)
    await query.answer("Вот платежные системы доступные для этой валюты")
    await window.pm(query.message)


@pay.callback_query(cd.Pm.filter(F.is_target))
async def h_got_target_pm(query: CallbackQuery, callback_data: cd.Pm, state: FSMContext):
    """Step 4f: Fill target cred.detail"""
    await query.message.delete()
    await state.update_data(t_pmcur_id=callback_data.pmcur_id, t_name=callback_data.name)
    await query.answer("Теперь нужны реквизиты")
    await window.fill_cred_dtl(query.message, state)


@pay.callback_query(cd.Cred.filter())
async def h_got_cred(query: CallbackQuery, callback_data: cd.Cred, state: FSMContext):
    await query.message.delete()
    await state.update_data(cred_id=callback_data.id)
    await query.answer("Теперь нужна сумма")
    await window.amount(query.message, state)


@pay.message(dep.CredState.detail)
async def h_got_cred_dtl(msg: Message, state: FSMContext):
    """Step 4.1f: Fill target cred.name"""
    while True:
        if msg.text.isdigit():
            await state.update_data(detail=int(msg.text))
            break
        else:
            await msg.answer("Пожалуйста, введите корректное число")
            return
    await window.fill_cred_name(msg, state)


@pay.message(dep.CredState.name)
async def h_got_cred_name(msg: Message, state: FSMContext):
    """Step 5f: Save target cred"""
    data = await state.get_data()
    await state.set_state(None)
    cred, _ = await models.Cred.update_or_create(
        {"name": msg.text}, detail=data["detail"], person_id=data["person_id"], pmcur_id=data["t_pmcur_id"]
    )
    await state.update_data(cred_id=cred.id)
    await window.amount(msg, state)


@pay.callback_query(cd.Ex.filter())
async def h_got_ex(query: CallbackQuery, callback_data: cd.Ex, state: FSMContext):
    """Step 4c: Save target"""
    await query.message.delete()
    if is_target := await state.get_value("is_target"):
        await state.update_data(t_name=callback_data.name)
    await state.update_data({("t" if is_target else "s") + "_ex_id": callback_data.id})
    await query.answer(f"Биржа {callback_data.name} выбрана")
    await (window.amount(query.message, state) if is_target else window.set_ppo(query.message))


@pay.message(dep.PaymentState.amount)
async def h_got_amount(msg: Message, state: FSMContext):
    """Step 6: Save target amount"""
    while True:
        if msg.text.isdigit():
            await state.update_data(amount=int(msg.text))
            break
        else:
            await msg.answer("Пожалуйста, введите корректное число")
            return
    await state.set_state(None)
    """Step 7: Select source type"""
    await state.update_data(is_target=False)
    if await state.get_value("is_fiat"):
        await window.type_select(msg, False)
    else:
        await window.cur_select(msg, state)  # сразу выбор валюты источника, тк если цель крипта


@pay.callback_query(cd.Pm.filter(F.is_target.__eq__(0)))
async def h_got_source_pm(query: CallbackQuery, callback_data: cd.Pm, state: FSMContext):
    await query.message.delete()
    await state.update_data(s_pmcur_id=callback_data.pmcur_id)
    await query.answer(callback_data.name)
    await window.set_ppo(query.message)


@pay.callback_query(cd.Ppo.filter())
async def h_got_ppo(query: CallbackQuery, state: FSMContext, callback_data: cd.Ppo):
    await query.message.delete()
    await state.update_data(ppo=callback_data.num)
    await query.answer(str(callback_data.num))
    await window.set_urgency(query.message)


@pay.callback_query(cd.Time.filter())
async def process_time_selection(callback: CallbackQuery, callback_data: cd.Time, state: FSMContext):
    await callback.answer()
    pay_until = datetime.now() + timedelta(minutes=callback_data.minutes)

    data = await state.get_data()
    if ex_id := data.get("t_ex_id", data.get("s_ex_id")):
        if not (actor_id := data.get("actor_id")):
            person_id = data.get("person_id")
            actor_id = await models.Actor.get(ex_id=ex_id, person_id=person_id).values_list("id", flat=True)
            await state.update_data(actor_id=actor_id)
        if not (addr_id := data.get("addr_id")):
            coin_id = data.get("t_coin_id", data.get("s_coin_id"))
            addr_id = await models.Addr.get(coin_id=coin_id, actor_id=actor_id).values_list("id", flat=True)
            await state.update_data(addr_id=addr_id)
    else:
        addr_id = None

    pay_req = await models.PayReq.create(
        pay_until=pay_until,
        amount=data["amount"],
        parts=data["ppo"],
        payed_at=None,
        addr_id=addr_id,
        cred_id=data["cred_id"],
        user_id=1,
    )
    await state.update_data(
        timer=callback_data.minutes,
        timer_active=True,
        pay_until=pay_until,
        pay_req_id=pay_req.id,
    )

    await state.set_state(dep.PaymentState.timer)
    create_task(window.run_timer(callback.message, state))


# ACTIONS
@pay.callback_query(cd.Action.filter(F.act.__eq__(cd.ActionType.received)))
async def payment_confirmed(query: CallbackQuery, state: FSMContext):
    await query.answer()
    payed_at = datetime.now()
    await state.update_data(timer_active=False, payed_at_formatted=payed_at)
    data = await state.get_data()
    if data.get("pay_req_id"):
        pay_req = await models.PayReq.get(id=data["pay_req_id"])
        pay_req.payed_at = payed_at
        await pay_req.save()

    builder = InlineKeyboardBuilder()
    builder.button(text="Новый платеж💸", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    await query.message.answer("✅ Платеж успешно подтвержден", reply_markup=builder.as_markup())
    await query.message.delete()
    await state.clear()


@pay.callback_query(cd.Action.filter(F.act.__eq__(cd.ActionType.not_received)))
async def no_payment(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(timer_active=False)
    await query.message.edit_text("Платеж не получен!")
    await query.message.answer("укажите детали платежа")
    await state.clear()
    await state.set_state(dep.Report.text)


@pay.message(dep.Report.text)
async def payment_not_specified(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    data = await state.get_data()
    complaint_text = (
        f"Жалоба на неполученный платеж:\n"
        f"Пользователь: @{msg.from_user.username or msg.from_user.id}\n"
        f"Детали платежа: {data["text"]}\n"
        f"Время: {msg.date.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await msg.bot.send_message(chat_id="1779829771", text=complaint_text)


# NAVIGATION
@pay.callback_query(cd.PayNav.filter(F.to.in_([cd.PayStep.t_type, cd.PayStep.s_type])))
async def handle_home(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await window.type_select(query.message, await state.get_value("is_target"))


@pay.callback_query(cd.PayNav.filter(F.to.in_([cd.PayStep.t_coin, cd.PayStep.s_coin])))
async def to_coin_select(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    is_target = await state.get_value("is_target")
    pref = "t" if is_target else "s"
    await state.update_data({pref + "_ex_id": None, pref + "_coin_id": None})
    await window.coin_select(query.message, state)


@pay.callback_query(cd.PayNav.filter(F.to.in_([cd.PayStep.t_cur, cd.PayStep.s_cur])))
async def to_cur_select(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    is_target = await state.get_value("is_target")
    pref = "t" if is_target else "s"
    await state.update_data({pref + "_pmcur_id": None, pref + "_cur_id": None})
    await window.cur_select(query.message, state)


@pay.callback_query(cd.PayNav.filter(F.to.in_([cd.PayStep.t_pm, cd.PayStep.s_pm])))
async def to_pm_select(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await window.pm(query.message, state)


@pay.callback_query(cd.PayNav.filter(F.to.__eq__(cd.PayStep.t_cred_dtl)))
async def back_to_cred_detail(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(detail=None)
    await window.fill_cred_dtl(query.message, state)
    await query.message.delete()


@pay.callback_query(cd.PayNav.filter(F.to.__eq__(cd.PayStep.t_cred_name)))
async def back_to_cred_name(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await state.update_data(name=None)
    await window.fill_cred_name(query.message, state)
    await query.message.delete()


@pay.callback_query(cd.PayNav.filter(F.to.in_([cd.PayStep.t_ex, cd.PayStep.s_ex])))
async def back_to_ex_select(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await state.update_data({("t" if await state.get_value("is_target") else "s") + "ex_id": None})
    await window.ex_select(query.message, state)


@pay.callback_query(cd.PayNav.filter(F.to.__eq__(cd.PayStep.t_amount)))
async def back_to_amount(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await state.update_data(amount=None)
    await window.amount(query.message, state)


@pay.callback_query(cd.PayNav.filter(F.to.in_([cd.PayStep.t_pm])))
async def back_to_payment(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await state.update_data(payment=None)
    await window.pm(query.message, state)
