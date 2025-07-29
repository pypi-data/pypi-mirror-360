# Persian Jalali Calendar

A simple, accurate, and lightweight Python library for the Persian (Jalali/Shamsi) calendar with no external dependencies.

This library allows for easy conversion between Jalali and Gregorian dates, provides date arithmetic, and offers helpful methods for formatting and date information, all through an intuitive API modeled after Python's built-in `datetime` module.

## Installation

Install the library from PyPI using pip:

```bash
pip install persian-jalali-calendar
```

## In-Depth Usage

### `JalaliDate` - The Core Object

The `JalaliDate` object is the heart of the library.

```python
from jalali_calendar import JalaliDate
import datetime

# --- Creating a Date ---

# 1. From year, month, and day
d = JalaliDate(1404, 4, 13)
print(d)  # Output: 1404-04-13

# 2. From today's system date
today = JalaliDate.today()
print(f"Today is: {today}")

# 3. From a standard Python datetime.date object
g_date = datetime.date(2025, 7, 4)
j_date = JalaliDate.from_gregorian(g_date)
print(f"Gregorian {g_date} is Jalali {j_date}")
```

### Conversion

Seamlessly convert back and forth.

```python
j_date = JalaliDate(1404, 4, 13)
g_date = j_date.to_gregorian()
print(g_date)  # Output: 2025-07-04
print(type(g_date)) # Output: <class 'datetime.date'>
```

### Accessing Properties

Get detailed information about any date.

```python
d = JalaliDate(1403, 1, 1) # Nowruz 1403

# Basic Properties
print(f"Year: {d.year}, Month: {d.month}, Day: {d.day}")

# Weekday Information (Saturday = 0, Friday = 6)
print(f"Weekday Number: {d.weekday()}")    # Output: 4 (Wednesday)
print(f"Weekday Name: {d.weekday_name()}") # Output: چهارشنبه

# Month Information
print(f"Month Name: {d.month_name()}")     # Output: فروردین

# Year Information
print(f"Is Leap Year? {d.is_leap()}")      # Output: True
print(f"Day of Year: {d.day_of_year()}")   # Output: 1
print(f"Week of Year: {d.week_number()}")  # Output: 1
```

### Formatting with `strftime`

Create custom-formatted strings.

```python
d = JalaliDate(1404, 4, 13)
# %A: Full weekday name, %d: Day, %B: Full month name, %Y: Year
formatted = d.strftime("%A، %d %B %Y")
print(formatted) # Output: جمعه، ۱۳ تیر ۱۴۰۴
```

### Arithmetic and Comparison

Use standard Python operators for date math.

```python
d1 = JalaliDate(1404, 4, 13)
d2 = d1 - datetime.timedelta(days=10)
print(f"10 days before {d1} was {d2}") # Output: 10 days before 1404-04-13 was 1404-04-03

time_diff = d1 - d2
print(f"Difference is {time_diff.days} days") # Output: 10

# All comparison operators work
print(f"Is d1 after d2? {d1 > d2}") # Output: True
```

### `JalaliDateTime`

For working with both date and time.

```python
from jalali_calendar import JalaliDateTime, JalaliDate
import datetime

# Create from components
dt = JalaliDateTime(1404, 5, 3, 15, 30, 0)
print(dt) # Output: 1404-05-03 15:30:00

# Get the current date and time
now = JalaliDateTime.now()
print(f"Now: {now}")

# Combine existing objects
d = JalaliDate(1399, 11, 22)
t = datetime.time(10, 0)
dt_combined = JalaliDateTime.combine(d, t)
print(dt_combined) # Output: 1399-11-22 10:00:00
```

## License

This project is licensed under the MIT License.