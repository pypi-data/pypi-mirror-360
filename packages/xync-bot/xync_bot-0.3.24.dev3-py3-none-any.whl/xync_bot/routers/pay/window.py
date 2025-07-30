from asyncio import sleep

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tortoise.functions import Max
from xync_schema import models

from xync_bot.routers.pay import cd, dep


async def type_select(msg: Message, is_target: bool):
    """Step 1: Select type"""
    if is_target is False:
        await msg.bot.delete_messages(chat_id=msg.chat.id, message_ids=[msg.message_id, msg.message_id - 1])
    rm = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Банковская валюта", callback_data=cd.TargetType(is_fiat=1, is_target=is_target).pack()
                ),
                InlineKeyboardButton(text="Крипта", callback_data=cd.TargetType(is_fiat=0, is_target=is_target).pack()),
            ]
        ]
    )
    await msg.answer("Что нужно?" if is_target else "Чем платишь?", reply_markup=rm)


async def amount(msg: Message, state: FSMContext):
    await msg.bot.delete_messages(chat_id=msg.chat.id, message_ids=[msg.message_id, msg.message_id - 1])
    """Step 5: Filling target amount"""
    builder = InlineKeyboardBuilder()

    if await state.get_value("is_fiat"):
        cur_coin = (await state.get_value("curs"))[await state.get_value("t_cur_id")]
        builder.button(text="Назад к вводу имени", callback_data=cd.PayNav(to=cd.PayStep.t_cred_name))
    else:
        cur_coin = (await state.get_value("coins"))[await state.get_value("t_coin_id")]
        builder.button(text="Назад к выбору биржи", callback_data=cd.PayNav(to=cd.PayStep.t_ex))

    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2)

    await msg.answer(
        f"Введите нужную сумму {cur_coin} для {await state.get_value('t_name')}", reply_markup=builder.as_markup()
    )
    await state.set_state(dep.PaymentState.amount)


async def cur_select(msg: Message, state: FSMContext):
    """Common using cur func"""
    if not (curs := await state.get_value("curs")):
        await state.update_data(curs=curs)
    builder = InlineKeyboardBuilder()
    is_target = await state.get_value("is_target")
    for cur_id, ticker in curs.items():
        builder.button(text=ticker + dep.flags[ticker], callback_data=cd.Cur(id=cur_id, is_target=is_target))
    builder.button(text="Назад к выбору типа", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(3, 3, 3, 3, 3, 1)
    sfx = "ую нужно" if is_target else "ой платишь"
    await msg.answer("Выбери валюту котор" + sfx, reply_markup=builder.as_markup())


async def coin_select(msg: Message, state: FSMContext):
    """Common using coin func"""
    builder = InlineKeyboardBuilder()
    if not (coins := await state.get_value("coins")):
        coins = {k: v for k, v in await models.Coin.all().values_list("id", "ticker")}
        await state.update_data(coins=coins)
    is_target = await state.get_value("is_target")
    for coin_id, ticker in coins.items():
        builder.button(text=ticker, callback_data=cd.Coin(id=coin_id, is_target=is_target))
    builder.button(
        text="Назад к выбору типа", callback_data=cd.PayNav(to=cd.PayStep.t_type if is_target else cd.PayStep.s_type)
    )
    builder.adjust(1)
    sfx = "ую нужно" if is_target else "ой платишь"
    await msg.answer("Выберите монету котор" + sfx, reply_markup=builder.as_markup())


async def ex_select(msg: Message, state: FSMContext):
    data = await state.get_data()
    is_target = data["is_target"]
    coin_id = data[("t" if is_target else "s") + "_coin_id"]
    if not (exs := data.get("exs", {}).get(coin_id)):
        await state.update_data({"exs": {coin_id: exs}})
    builder = InlineKeyboardBuilder()
    for eid, name in exs:
        builder.button(text=name, callback_data=cd.Ex(id=eid, name=name, is_target=is_target))
    builder.button(
        text="Назад к выбору монеты", callback_data=cd.PayNav(to=cd.PayStep.t_coin if is_target else cd.PayStep.s_coin)
    )
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(1)
    keyboard = builder.as_markup()
    await msg.answer("На какую биржу?" if is_target else "С какой биржи?", reply_markup=keyboard)


async def pm(msg: Message, state: FSMContext):
    data = await state.get_data()
    is_target = data["is_target"]
    cur_id = data[("t" if is_target else "s") + "_cur_id"]
    if not (pms := data.get("pms", {}).get(cur_id)):
        pms = await (
            models.Pmex.filter(pm__pmcurs__cur_id=cur_id)
            .annotate(lname=Max("name"))
            .group_by("pm__pmcurs__id")
            .values_list("pm__pmcurs__id", "lname")
        )
        await state.update_data({"pms": {cur_id: pms}})
    builder = InlineKeyboardBuilder()
    for pmcur_id, name in pms:
        builder.button(text=name, callback_data=cd.Pm(pmcur_id=pmcur_id, name=name[:50], is_target=is_target))
    builder.button(
        text="Назад к выбору валюты", callback_data=cd.PayNav(to=cd.PayStep.t_cur if is_target else cd.PayStep.s_cur)
    )
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(1)
    keyboard = builder.as_markup()
    txt = "На какую платежную систему?" if is_target else "C какой платежной системы?"
    await msg.answer(txt, reply_markup=keyboard)


async def fill_cred_dtl(msg: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    data = await state.get_data()
    if not (person_id := data.get("person_id")):
        person_id = await models.User.get(username_id=193017646).values_list("person_id", flat=True)
        await state.update_data(person_id=person_id)
    pmcur_id = data["t_pmcur_id"]
    if not (creds := data.get("creds", {}).get(pmcur_id)):
        creds = await models.Cred.filter(person_id=person_id, pmcur_id=pmcur_id)
        await state.update_data({"creds": {pmcur_id: creds}})
    for cred in creds:
        txt = f"{cred.detail}\n{cred.name}"
        if cred.extra:
            txt += f" ({cred.extra})"
        builder.button(text=txt, callback_data=cd.Cred(id=cred.id))

    builder.button(text="Назад к выбору платежной системы", callback_data=cd.PayNav(to=cd.PayStep.t_pm))
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2)
    txt = "Выберите реквизиты куда нужно получить деньги, если в списке нет нужных, то\n"
    await msg.answer(f"{txt}Введите номер для {await state.get_value('t_name')}:", reply_markup=builder.as_markup())
    await state.set_state(dep.CredState.detail)


async def fill_cred_name(msg: Message, state: FSMContext):
    await msg.bot.delete_messages(chat_id=msg.chat.id, message_ids=[msg.message_id, msg.message_id - 1])
    await state.update_data(detail=msg.text)
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад к вводу реквизитов", callback_data=cd.PayNav(to=cd.PayStep.t_cred_dtl))
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2)
    data = await state.get_data()
    cur = data["curs"].get(data["t_cur_id"])
    payment = data["t_name"]
    detail = data["detail"]
    await msg.answer(f"{cur}:{payment}:{detail}: Введите имя получателя", reply_markup=builder.as_markup())
    await state.set_state(dep.CredState.name)


async def set_ppo(msg: Message):
    rm = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data="ppo:1"),
                InlineKeyboardButton(text="Да", callback_data="ppo:2"),
            ],
            [InlineKeyboardButton(text="Да хоть на 3", callback_data="ppo:3")],
        ]
    )
    await msg.answer("На 2 платежа сможем разбить?", reply_markup=rm)


async def set_urgency(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="1 мин", callback_data=cd.Time(minutes=1))
    builder.button(text="5 мин", callback_data=cd.Time(minutes=5))
    builder.button(text="30 мин", callback_data=cd.Time(minutes=30))
    builder.button(text="3 часа", callback_data=cd.Time(minutes=180))
    builder.button(text="сутки", callback_data=cd.Time(minutes=60 * 24))
    builder.button(text="Назад к вводу платежей", callback_data=cd.PayNav(to=cd.PayStep.t_pm))
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2, 2, 1, 1, 1)
    await msg.answer("Сколько можешь ждать?", reply_markup=builder.as_markup())


async def run_timer(message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="Платеж получен", callback_data=cd.Action(act=cd.ActionType.received))

    data = await state.get_value("timer")
    seconds = data * 60

    def format(sec):
        days = sec // (24 * 3600)
        sec %= 24 * 3600
        hours = sec // 3600
        sec %= 3600
        minutes = sec // 60
        sec %= 60

        if days > 0:
            return f"{days}д {hours:02d}:{minutes:02d}:{sec:02d}"
        elif hours > 0:
            return f"{hours:02d}:{minutes:02d}:{sec:02d}"
        else:
            return f"{minutes:02d}:{sec:02d}"

    try:
        await message.edit_text(f"⏳ Осталось {format(seconds)}", reply_markup=builder.as_markup())
    except Exception:
        return

    while seconds > 0:
        await sleep(1)
        seconds -= 1
        try:
            await message.edit_text(f"⏳ Осталось {format(seconds)}", reply_markup=builder.as_markup())
            await state.update_data(timer=seconds)
        except Exception:
            break

    if seconds <= 0:
        builder = InlineKeyboardBuilder()
        builder.button(text="Платеж получен", callback_data=cd.Action(act=cd.ActionType.received))
        builder.button(text="Денег нет", callback_data=cd.Action(act=cd.ActionType.not_received))
        try:
            await message.edit_text("⏳ Время вышло!", reply_markup=builder.as_markup())
        except Exception:
            pass
