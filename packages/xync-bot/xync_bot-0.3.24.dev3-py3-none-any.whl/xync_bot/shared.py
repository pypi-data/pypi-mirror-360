from aiogram.filters.callback_data import CallbackData


class NavCallbackData(CallbackData, prefix="nav"):  # navigate menu
    to: str
