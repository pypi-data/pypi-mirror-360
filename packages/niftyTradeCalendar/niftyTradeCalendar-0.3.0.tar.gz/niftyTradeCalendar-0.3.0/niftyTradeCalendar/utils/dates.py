import datetime
from ..data.holidays import HOLIDAYS

def get_all_thursdays(year):
    d = datetime.date(year, 1, 1)
    d += datetime.timedelta(days=(3 - d.weekday()) % 7)
    while d.year == year:
        yield d
        d += datetime.timedelta(days=7)

def adjust_expiry_to_working_day(date: datetime.date):
    holiday_dates = {h["date"] for h in HOLIDAYS}
    if date in holiday_dates:
        return date - datetime.timedelta(days=1)
    return date
