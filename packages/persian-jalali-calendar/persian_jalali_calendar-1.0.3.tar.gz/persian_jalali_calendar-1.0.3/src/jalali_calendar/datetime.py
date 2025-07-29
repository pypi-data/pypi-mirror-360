import datetime
from .date import JalaliDate

class JalaliDateTime:
    """
    An object representing a specific point in time (date and time)
    in the Jalali calendar.
    """
    def __init__(self, year, month, day, hour=0, minute=0, second=0):
        self._date = JalaliDate(year, month, day)
        
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError("Time component is out of range.")
        
        self._time = datetime.time(hour, minute, second)

    @property
    def year(self): return self._date.year
    @property
    def month(self): return self._date.month
    @property
    def day(self): return self._date.day
    @property
    def hour(self): return self._time.hour
    @property
    def minute(self): return self._time.minute
    @property
    def second(self): return self._time.second
    
    def date(self) -> JalaliDate:
        """Returns the JalaliDate part of the datetime."""
        return self._date

    def time(self) -> datetime.time:
        """Returns the standard Python datetime.time part of the datetime."""
        return self._time
        
    def __repr__(self) -> str:
        return (
            f"JalaliDateTime({self.year}, {self.month}, {self.day}, "
            f"{self.hour}, {self.minute}, {self.second})"
        )

    def __str__(self) -> str:
        return f"{self._date} {self._time}"

    @classmethod
    def now(cls):
        """Creates a JalaliDateTime object from the current system date and time."""
        now = datetime.datetime.now()
        j_date = JalaliDate.from_gregorian(now.date())
        return cls.combine(j_date, now.time())

    @classmethod
    def combine(cls, date: JalaliDate, time: datetime.time):
        """Creates a JalaliDateTime object from a JalaliDate and a datetime.time object."""
        if not isinstance(date, JalaliDate) or not isinstance(time, datetime.time):
            raise TypeError("Invalid types for date or time.")
        
        return cls(date.year, date.month, date.day, time.hour, time.minute, time.second)