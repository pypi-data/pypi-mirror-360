from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callback import CalendarCallback
from .utils import get_month_days, month_name, DAYS
from .calendar_types import DateIconMap

def build_year_selector(base_year: int) -> InlineKeyboardMarkup:
    years_range = range(base_year - 4, base_year + 5)
    keyboard = []

    for i in range(0, len(years_range), 3):
        row = []
        for j in range(3):
            if i + j < len(years_range):
                y = years_range[i + j]
                row.append(
                    InlineKeyboardButton(
                        text=str(y),
                        callback_data=CalendarCallback(action="select_year", year=y, month=0).pack()
                    )
                )
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            text="<<",
            callback_data=CalendarCallback(action="change_year_range", year=base_year - 9, month=0).pack()
        ),
        InlineKeyboardButton(
            text=">>",
            callback_data=CalendarCallback(action="change_year_range", year=base_year + 9, month=0).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_month_selector(year: int) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(1, 13, 3):
        row = []
        for j in range(3):
            month_num = i + j
            if month_num > 12:
                break
            row.append(
                InlineKeyboardButton(
                    text=month_name(month_num),
                    callback_data=CalendarCallback(action="select_month", year=year, month=month_num).pack()
                )
            )
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            text="<<",
            callback_data=CalendarCallback(action="select_year", year=year - 1, month=0).pack()
        ),
        InlineKeyboardButton(
            text=str(year),
            callback_data=CalendarCallback(action="show_years", year=year, month=0).pack()
        ),
        InlineKeyboardButton(
            text=">>",
            callback_data=CalendarCallback(action="select_year", year=year + 1, month=0).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_calendar(year: int, month: int, icon_dates: DateIconMap = None) -> InlineKeyboardMarkup:
    icon_dates = icon_dates or {}
    kb = []

    prev_month = month - 1 if month > 1 else 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    kb.append([
        InlineKeyboardButton(text="<<", callback_data=CalendarCallback(action="select_month", year=prev_year, month=prev_month).pack()),
        InlineKeyboardButton(text=f"{month_name(month)} {year}", callback_data=CalendarCallback(action="show_months", year=year, month=month).pack()),
        InlineKeyboardButton(text=">>", callback_data=CalendarCallback(action="select_month", year=next_year, month=next_month).pack()),
    ])

    kb.append([InlineKeyboardButton(text=d, callback_data="ignore") for d in DAYS])

    for week in get_month_days(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                icon = icon_dates.get(date_str, "")
                icon_display = icon if icon else " "
                text = f"{day:>2} {icon_display}"

                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=CalendarCallback(
                            action="select_day", year=year, month=month, day=day
                        ).pack()
                    )
                )
        kb.append(row)

    kb.append([
        InlineKeyboardButton(text="📆 Годы", callback_data=CalendarCallback(action="show_years", year=year, month=month).pack())
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)
