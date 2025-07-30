from enum import IntEnum

from aiogram.fsm.state import StatesGroup, State


class Report(StatesGroup):
    text = State()


class CredState(StatesGroup):
    detail = State()
    name = State()


class PaymentState(StatesGroup):
    amount = State()
    timer = State()
    timer_active = State()


class ActionType(IntEnum):
    """Цель (назначение) платежа (target)"""

    sent = 1  # Отправил
    received = 2  # Получил
    not_received = 3  # Не получил


class PayStep(IntEnum):
    """Цель (назначение) платежа (target)"""

    t_type = 1  # Выбор типа
    t_cur = 2  # Выбор валюты
    t_coin = 3  # Выбор монеты
    t_pm = 4  # Выбор платежки
    t_ex = 5  # Выбор биржи
    t_cred_dtl = 6  # Ввод номера карты
    t_cred_name = 7  # Ввод имени
    # t_addr = 8 # todo: позже добавим: Выбор/ввод крипто кошелька
    t_amount = 9  # Ввод суммы
    """ Источник платежа (source) """
    s_type = 10  # Выбор типа
    s_cur = 11  # Выбор типа
    s_pm = 12  # Выбор типа
    s_coin = 13  # Выбор типа
    s_ex = 14  # Выбор типа
    ppo = 15  # Выбор возможности разбивки платежа
    urgency = 16  # Выбор срочности получения платежа
    pending_send = 17  # Ожидание отправки (если мы платим фиатом)
    pending_confirm = 18  # Ожидание пока на той стороне подтвердят получение нашего фиата (если мы платим фиатом)
    pending_receive = 19  # Ожидание поступления (если мы получаем фиат)


flags = {
    "RUB": "🇷🇺",
    "THB": "🇹🇭",
    "IDR": "🇮🇩",
    "TRY": "🇹🇷",
    "GEL": "🇬🇪",
    "VND": "🇻🇳",
    "AED": "🇦🇪",
    "AMD": "🇦🇲",
    "AZN": "🇦🇿",
    "CNY": "🇨🇳",
    "EUR": "🇪🇺",
    "HKD": "🇭🇰",
    "INR": "🇮🇳",
    "PHP": "🇵🇭",
    "USD": "🇺🇸",
}
