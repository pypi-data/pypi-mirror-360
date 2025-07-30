# niftyTradeCalendar

A Python package to provide holiday and expiry calendars for Indian markets (NIFTY).  
It helps you determine trading days, check for holidays, and compute weekly expiry dates, considering official exchange holidays.

## Features

- List all trading days for a given year, excluding weekends and exchange holidays.
- Check if a specific date is a trading holiday.
- Get all weekly expiry dates (typically Thursdays), automatically adjusted for holidays.

## Installation

```sh
pip install setuptools wheel twine
python3 setup.py sdist bdist_wheel
pip install dist/niftyTradeCalendar-*.whl
```

## Usage

```python
import datetime
from niftyTradeCalendar import is_holiday, get_trading_days, get_weekly_expiry_dates

# Check if a date is a holiday
print(is_holiday(datetime.date(2024, 1, 26)))  # True

# Get all trading days for 2024
trading_days = get_trading_days(2024)
print(trading_days[:5])  # First 5 trading days

# Get weekly expiry dates for 2024
expiry_dates = get_weekly_expiry_dates(2024)
print(expiry_dates[:5])  # First 5 expiry dates
```

## Running Tests

```sh
pytest tests/
```

## Project Structure

```
niftyTradeCalendar/
    __init__.py
    main.py
    data/
        holidays.py
    utils/
        dates.py
tests/
    test_calendar.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Sonu Kumar  
[GitHub](https://github.com/skrdeveloper1/niftyTradeCalendar) | [LinkedIn](https://in.linkedin.com/in/skrdeveloper1)
