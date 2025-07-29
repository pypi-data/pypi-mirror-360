from aiogram.filters.callback_data import CallbackData

class CalendarCallback(CallbackData, prefix="calendar"):
    action: str
    year: int
    month: int
    day: int = 0
