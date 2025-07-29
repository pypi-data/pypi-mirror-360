import calendar


# def month_name(month: int) -> str:
#     return calendar.month_name[month]


def month_name(month: int) -> str:
    months_ru = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    return months_ru[month - 1]


def get_month_days(year: int, month: int):
    return calendar.monthcalendar(year, month)

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
