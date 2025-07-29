# Persian Jalali Calendar

A simple, accurate, and lightweight Python library for the Persian Jalali calendar with no external dependencies.

This library allows for easy conversion between Jalali and Gregorian dates, provides date arithmetic, and offers helpful methods for formatting and date information, all through an intuitive API modeled after Python's `datetime` module.

## Installation

Install the library from PyPI using pip:

```bash
pip install persian-jalali-calendar
```

## Quick Start

### Creating a `JalaliDate` Object

```python
from jalali_calendar import JalaliDate
import datetime

# Create a Jalali date directly
d = JalaliDate(1404, 4, 13)
print(d)
# > 1404-04-13

# Get today's date
today = JalaliDate.today()
print(f"Today is: {today}")

# Create from a Gregorian datetime.date object
g_date = datetime.date(2025, 7, 4)
j_date = JalaliDate.from_gregorian(g_date)
print(f"Gregorian {g_date} is Jalali {j_date}")
# > Gregorian 2025-07-04 is Jalali 1404-04-13
```

### Converting Back to Gregorian

```python
from jalali_calendar import JalaliDate

j_date = JalaliDate(1404, 4, 13)
g_date = j_date.to_gregorian()

print(f"Jalali {j_date} is Gregorian {g_date}")
# > Jalali 1404-04-13 is Gregorian 2025-07-04
```

### Accessing Date Properties

```python
from jalali_calendar import JalaliDate

d = JalaliDate(1403, 1, 1) # Nowruz 1403

print(f"Year: {d.year}")         # > 1403
print(f"Month: {d.month}")       # > 1
print(f"Day: {d.day}")           # > 1
print(f"Weekday: {d.weekday()}") # > 4 (Wednesday, since Saturday=0)
print(f"Weekday Name: {d.weekday_name()}") # > چهارشنبه
print(f"Month Name: {d.month_name()}")   # > فروردین
print(f"Is Leap Year? {d.is_leap()}") # > True
```

### Formatting with `strftime`

Use `strftime` for custom string formatting, including Persian names.

```python
from jalali_calendar import JalaliDate

d = JalaliDate(1404, 4, 13)
formatted = d.strftime("%A، %d %B %Y")
print(formatted)
# > جمعه، ۱۳ تیر ۱۴۰۴
```

### Date Arithmetic

You can perform standard date arithmetic using `datetime.timedelta`.

```python
from jalali_calendar import JalaliDate
import datetime

d1 = JalaliDate(1404, 4, 13)
d2 = JalaliDate(1404, 4, 1)

# Subtract two Jalali dates to get a timedelta
time_diff = d1 - d2
print(f"Difference is {time_diff.days} days") # > 12

# Add or subtract a timedelta from a Jalali date
ten_days_later = d1 + datetime.timedelta(days=10)
print(f"10 days after {d1} is {ten_days_later}") # > 1404-04-23
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.