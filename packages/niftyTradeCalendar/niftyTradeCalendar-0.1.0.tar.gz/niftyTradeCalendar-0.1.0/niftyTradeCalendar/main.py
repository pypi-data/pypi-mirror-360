import datetime
from .data.holidays import HOLIDAYS
from .utils.dates import get_all_thursdays, adjust_expiry_to_working_day

def is_holiday(date: datetime.date) -> bool:
    return date in {h["date"] for h in HOLIDAYS}

def get_trading_days(year: int):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    days = []
    for i in range((end - start).days + 1):
        d = start + datetime.timedelta(days=i)
        if d.weekday() < 5 and not is_holiday(d):
            days.append(d)
    return days

def get_weekly_expiry_dates(year: int, symbol="NIFTY"):
    thursdays = get_all_thursdays(year)
    adjusted = [adjust_expiry_to_working_day(d) for d in thursdays]
    return adjusted
