# niftyTradeCalendar

**niftyTradeCalendar** is a Python package that provides official holiday and expiry calendars for Indian markets (NIFTY).  
It helps you determine trading days, check for holidays, and compute weekly expiry dates, considering official exchange holidays.

---

## Features

- **Trading Days**: List all trading days for a given year, excluding weekends and exchange holidays.
- **Holiday Checker**: Check if a specific date is a trading holiday.
- **Weekly Expiry Dates**: Get all weekly expiry dates (typically Thursdays), automatically adjusted for holidays.

---

## Installation

To build and install the package locally:

```sh
pip install setuptools wheel twine
python3 setup.py sdist bdist_wheel
pip install dist/niftyTradeCalendar-*.whl
```

---

## Usage

Import the main functions and use them as follows:

```python
import datetime
from niftyTradeCalendar import is_holiday, get_trading_days, get_weekly_expiry_dates

# Check if a date is a holiday
print(is_holiday(datetime.date(2024, 1, 26)))  # Output: True

# Get all trading days for 2024
trading_days = get_trading_days(2024)
print(trading_days[:5])  # First 5 trading days

# Get weekly expiry dates for 2024
expiry_dates = get_weekly_expiry_dates(2024)
print(expiry_dates[:5])  # First 5 expiry dates
```

---

## API Reference

- `is_holiday(date: datetime.date) -> bool`  
  Returns `True` if the given date is an exchange holiday.

- `get_trading_days(year: int) -> List[datetime.date]`  
  Returns a list of all trading days for the specified year.

- `get_weekly_expiry_dates(year: int, symbol="NIFTY") -> List[datetime.date]`  
  Returns a list of weekly expiry dates for the specified year, adjusted for holidays.

---

## Running Tests

To run the test suite:

```sh
pytest tests/
```

---

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

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/skrdeveloper1/niftyTradeCalendar).

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Sonu Kumar  
[GitHub](https://github.com/skrdeveloper1/niftyTradeCalendar) | [LinkedIn](https://in.linkedin.com/in/skrdeveloper1)

---

## Building and Publishing

To rebuild and upload a new release:

```sh
python3 setup.py sdist bdist_wheel
twine upload dist/*
```

```sh
pip uninstall niftyTradeCalendar
```

```sh
pip install niftyTradeCalendar
```
