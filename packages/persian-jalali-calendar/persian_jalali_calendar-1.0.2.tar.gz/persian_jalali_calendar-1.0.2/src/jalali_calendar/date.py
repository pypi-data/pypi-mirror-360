import datetime
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
    """
    An object representing a single date (year, month, day) in the Jalali calendar.
    """

    def __init__(self, year: int, month: int, day: int):
        """
        Creates a JalaliDate object.
        
        Raises:
            ValueError: If the date components are invalid.
        """

        if not (isinstance(year, int) and isinstance(month, int) and isinstance(day, int)):
            raise TypeError("year, month, and day must be integers.")
        
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")
            
        days_in_month = JALALI_MONTH_DAYS[month]
        if month == 12 and converter.is_jalali_leap(year):
            days_in_month = 30
        
        if day < 1 or day > days_in_month:
            raise ValueError(f"Day is out of range for month {month} in year {year}.")

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

    def __repr__(self) -> str:
        """The 'official' string representation, for debugging."""
        return f"JalaliDate({self._year}, {self._month}, {self._day})"

    def __str__(self) -> str:
        """The 'user-friendly' string representation."""
        return f"{self._year:04d}-{self._month:02d}-{self._day:02d}"

    @classmethod
    def today(cls):
        """Creates a JalaliDate object from the current system date."""
        g_today = datetime.date.today()
        j_year, j_month, j_day = converter.gregorian_to_jalali(
            g_today.year, g_today.month, g_today.day
        )
        return cls(j_year, j_month, j_day)

    @classmethod
    def from_gregorian(cls, g_date: datetime.date):
        """Creates a JalaliDate object from a standard Python datetime.date object."""
        if not isinstance(g_date, datetime.date):
            raise TypeError("Input must be a datetime.date object.")
            
        j_year, j_month, j_day = converter.gregorian_to_jalali(
            g_date.year, g_date.month, g_date.day
        )
        return cls(j_year, j_month, j_day)

    def to_gregorian(self) -> datetime.date:
        """Converts this JalaliDate object to a standard Python datetime.date object."""
        g_year, g_month, g_day = converter.jalali_to_gregorian(
            self._year, self._month, self._day
        )
        return datetime.date(g_year, g_month, g_day)

    def weekday(self) -> int:
        """
        Returns the day of the week as an integer, where Saturday is 0.
        (Saturday=0, Sunday=1, ..., Friday=6)
        """
        g_date = self.to_gregorian()

        g_weekday = g_date.weekday()

        return (g_weekday + 2) % 7
        
    def weekday_name(self) -> str:
        """Returns the full Persian name of the weekday (e.g., "شنبه")."""
        return PERSIAN_WEEKDAY_NAMES[self.weekday()]

    def month_name(self) -> str:
        """Returns the full Persian name of the month (e.g., "فروردین")."""
        return PERSIAN_MONTH_NAMES[self._month]
        
    def is_leap(self) -> bool:
        """Returns True if the date is in a Jalali leap year."""
        return converter.is_jalali_leap(self._year)

    def _to_ordinal(self) -> int:
        """A helper method to convert a date to a single integer for comparisons."""
        return converter.jalali_to_jdn(self._year, self._month, self._day)

    def __eq__(self, other):
        """Equality check: self == other"""
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() == other._to_ordinal()

    def __ne__(self, other):
        """Inequality check: self != other"""
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() != other._to_ordinal()

    def __lt__(self, other):
        """Less than check: self < other"""
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() < other._to_ordinal()

    def __le__(self, other):
        """Less than or equal check: self <= other"""
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() <= other._to_ordinal()

    def __gt__(self, other):
        """Greater than check: self > other"""
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() > other._to_ordinal()

    def __ge__(self, other):
        """Greater than or equal check: self >= other"""
        if not isinstance(other, JalaliDate):
            return NotImplemented
        return self._to_ordinal() >= other._to_ordinal()

    def __add__(self, other):
        """Addition with a timedelta: self + timedelta(days=n)"""
        if not isinstance(other, datetime.timedelta):
            return NotImplemented

        jdn = self._to_ordinal() + other.days
        j_year, j_month, j_day = converter.jdn_to_jalali(jdn)
        return JalaliDate(j_year, j_month, j_day)

    def __sub__(self, other):
        """Subtraction: self - other"""
        if isinstance(other, datetime.timedelta):

            jdn = self._to_ordinal() - other.days
            j_year, j_month, j_day = converter.jdn_to_jalali(jdn)
            return JalaliDate(j_year, j_month, j_day)
        
        if isinstance(other, JalaliDate):

            return datetime.timedelta(days=self._to_ordinal() - other._to_ordinal())
            
        return NotImplemented

    def strftime(self, fmt: str) -> str:
        """
        Format the date into a string according to a format string.
        - %Y: Year (e.g., 1404)
        - %m: Month as a zero-padded number (e.g., 04)
        - %d: Day as a zero-padded number (e.g., 13)
        - %B: Full Persian month name (e.g., تیر)
        - %A: Full Persian weekday name (e.g., جمعه)
        - %y: Two-digit year (e.g., 04)
        - %-m: Month as a number (e.g., 4)
        - %-d: Day as a number (e.g., 13)
        """

        return fmt.replace('%Y', str(self._year)) \
                  .replace('%y', str(self._year)[-2:]) \
                  .replace('%B', self.month_name()) \
                  .replace('%m', f"{self._month:02d}") \
                  .replace('%-m', str(self._month)) \
                  .replace('%A', self.weekday_name()) \
                  .replace('%d', f"{self._day:02d}") \
                  .replace('%-d', str(self._day))

    def day_of_year(self) -> int:
        """Returns the day number within the year (1-365 or 1-366)."""
        first_day_of_year_jdn = converter.jalali_to_jdn(self._year, 1, 1)
        current_jdn = self._to_ordinal()
        return current_jdn - first_day_of_year_jdn + 1
    
    def week_number(self) -> int:
        """
        Returns the week number of the year (1-53).
        Week 1 is the first week containing a Saturday.
        """
        doy = self.day_of_year()

        first_day_gregorian = converter.jalali_to_gregorian(self._year, 1, 1)

        g_weekday = datetime.date(*first_day_gregorian).weekday() 

        first_day_weekday = (g_weekday + 2) % 7

        return ((doy + first_day_weekday - 1) // 7) + 1