import datetime
import re
from . import converter

JALALI_MONTH_DAYS = [0, 31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
PERSIAN_MONTH_NAMES = [
    "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]
PERSIAN_WEEKDAY_NAMES = [
    "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"
]


class JalaliDate:
    """An object representing a single date (year, month, day) in the Jalali calendar."""

    def __init__(self, year: int, month: int, day: int):
        if not (isinstance(year, int) and isinstance(month, int) and
                isinstance(day, int)):
            raise TypeError("year, month, and day must be integers.")

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")

        days_in_month = JALALI_MONTH_DAYS[month]
        if month == 12 and converter.is_jalali_leap(year):
            days_in_month = 30

        if day < 1 or day > days_in_month:
            raise ValueError(
                f"Day is out of range for month {month} in year {year}."
            )

        self._year = year
        self._month = month
        self._day = day

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    def __repr__(self):
        return f"JalaliDate({self._year}, {self._month}, {self._day})"

    def __str__(self):
        return f"{self._year:04d}-{self._month:02d}-{self._day:02d}"

    @classmethod
    def today(cls):
        g_today = datetime.date.today()
        j_year, j_month, j_day = converter.gregorian_to_jalali(
            g_today.year, g_today.month, g_today.day
        )
        return cls(j_year, j_month, j_day)

    @classmethod
    def from_gregorian(cls, g_date: datetime.date):
        if not isinstance(g_date, datetime.date):
            raise TypeError("Input must be a datetime.date object.")
        j_year, j_month, j_day = converter.gregorian_to_jalali(
            g_date.year, g_date.month, g_date.day
        )
        return cls(j_year, j_month, j_day)

    def to_gregorian(self) -> datetime.date:
        g_year, g_month, g_day = converter.jalali_to_gregorian(
            self._year, self._month, self._day
        )
        return datetime.date(g_year, g_month, g_day)

    def weekday(self) -> int:
        g_date = self.to_gregorian()
        g_weekday = g_date.weekday()
        return (g_weekday + 2) % 7

    def weekday_name(self) -> str:
        return PERSIAN_WEEKDAY_NAMES[self.weekday()]

    def month_name(self) -> str:
        return PERSIAN_MONTH_NAMES[self._month]

    def is_leap(self) -> bool:
        return converter.is_jalali_leap(self._year)

    def _to_ordinal(self) -> int:
        return converter.jalali_to_jdn(self._year, self._month, self._day)

    def __eq__(self, other):
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() == other._to_ordinal()

    def __ne__(self, other):
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() != other._to_ordinal()

    def __lt__(self, other):
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() < other._to_ordinal()

    def __le__(self, other):
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() <= other._to_ordinal()

    def __gt__(self, other):
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() > other._to_ordinal()

    def __ge__(self, other):
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() >= other._to_ordinal()

    def __add__(self, other):
        if not isinstance(other, datetime.timedelta):
            return NotImplemented
        jdn = self._to_ordinal() + other.days
        j_year, j_month, j_day = converter.jdn_to_jalali(jdn)
        return JalaliDate(j_year, j_month, j_day)

    def __sub__(self, other):
        if isinstance(other, datetime.timedelta):
            jdn = self._to_ordinal() - other.days
            j_year, j_month, j_day = converter.jdn_to_jalali(jdn)
            return JalaliDate(j_year, j_month, j_day)
        if isinstance(other, JalaliDate):
            return datetime.timedelta(
                days=self._to_ordinal() - other._to_ordinal()
            )
        return NotImplemented

    def strftime(self, fmt: str) -> str:
        g_date = self.to_gregorian()
        out = fmt.replace('%B', self.month_name())
        out = out.replace('%A', self.weekday_name())
        out = out.replace('%Y', str(self._year))
        out = out.replace('%y', str(self._year)[-2:])
        out = out.replace('%m', f"{self._month:02d}")
        out = out.replace('%-m', str(self._month))
        out = out.replace('%d', f"{self._day:02d}")
        out = out.replace('%-d', str(self._day))
        out = out.replace('%w', str(self.weekday()))
        out = out.replace('%j', f"{self.day_of_year():03d}")
        out = out.replace('%U', g_date.strftime('%U'))
        out = out.replace('%W', g_date.strftime('%W'))
        return out

    def day_of_year(self) -> int:
        first_day_of_year_jdn = converter.jalali_to_jdn(self._year, 1, 1)
        current_jdn = self._to_ordinal()
        return current_jdn - first_day_of_year_jdn + 1

    def week_number(self) -> int:
        doy = self.day_of_year()
        first_day_of_year = JalaliDate(self._year, 1, 1)
        first_day_weekday = first_day_of_year.weekday()
        return ((doy + first_day_weekday - 1) // 7) + 1

    @classmethod
    def strptime(cls, date_string: str, fmt: str):
        format_map = {
            '%Y': r'(?P<Y>\d{4})',
            '%y': r'(?P<y>\d{2})',
            '%m': r'(?P<m>\d{1,2})',
            '%-m': r'(?P<m>\d{1,2})',
            '%d': r'(?P<d>\d{1,2})',
            '%-d': r'(?P<d>\d{1,2})',
            '%B': r'(?P<B>[\u0600-\u06FF\s]+)',
        }
        pattern = fmt
        for code, regex in format_map.items():
            pattern = pattern.replace(code, regex)

        match = re.match(pattern, date_string)
        if not match:
            raise ValueError(
                f"Date string '{date_string}' does not match format '{fmt}'"
            )
        data = match.groupdict()
        year = int(data.get('Y') or f"13{data.get('y')}")
        day = int(data.get('d'))
        month_str = data.get('m')
        if month_str:
            month = int(month_str)
        else:
            month_name = data.get('B').strip()
            try:
                month = PERSIAN_MONTH_NAMES.index(month_name)
            except ValueError:
                raise ValueError(f"Unknown month name: '{month_name}'")
        return cls(year, month, day)

    def add_months(self, months_to_add: int):
        total_months = self._month + months_to_add
        year_delta, new_month = divmod(total_months - 1, 12)
        new_year = self._year + year_delta
        new_month += 1
        days_in_new_month = JALALI_MONTH_DAYS[new_month]
        if new_month == 12 and converter.is_jalali_leap(new_year):
            days_in_new_month = 30
        new_day = min(self._day, days_in_new_month)
        return JalaliDate(new_year, new_month, new_day)

    def add_years(self, years_to_add: int):
        new_year = self._year + years_to_add
        new_day = self._day
        if (self._month == 12 and self._day == 30 and
                not converter.is_jalali_leap(new_year)):
            new_day = 29
        return JalaliDate(new_year, self._month, new_day)