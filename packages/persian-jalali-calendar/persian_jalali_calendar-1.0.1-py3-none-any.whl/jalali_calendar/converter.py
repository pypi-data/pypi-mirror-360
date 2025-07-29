def is_gregorian_leap(year: int) -> bool:
    """Checks if a given Gregorian year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def is_jalali_leap(year: int) -> bool:
    """
    Checks if a given Jalali year is a leap year based on the 33-year cycle.
    A Jalali year is a leap year if (year % 33) is in a specific set of numbers.
    """
    leap_remainders = {1, 5, 9, 13, 17, 22, 26, 30}
    return (year % 33) in leap_remainders

JALALI_EPOCH_JDN = 1948320

def gregorian_to_jdn(gy: int, gm: int, gd: int) -> int:
    """Converts a Gregorian date to its Julian Day Number."""

    a = (14 - gm) // 12
    y = gy + 4800 - a
    m = gm + 12 * a - 3
    jdn = gd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn

def jdn_to_gregorian(jdn: int) -> tuple[int, int, int]:
    """Converts a Julian Day Number to its Gregorian date."""

    p = jdn + 68569
    q = 4 * p // 146097
    r = p - (146097 * q + 3) // 4
    s = 4000 * (r + 1) // 1461001
    t = r - 1461 * s // 4 + 31
    u = 80 * t // 2447
    gd = t - 2447 * u // 80
    v = u // 11
    gm = u + 2 - 12 * v
    gy = 100 * (q - 49) + s + v
    return gy, gm, gd

def jalali_to_jdn(jy: int, jm: int, jd: int) -> int:
    """Converts a Jalali date to its Julian Day Number."""
    days_in_year = (jy - 1) * 365

    leap_years = 0
    if jy > 1:

        num_cycles = (jy - 1) // 33
        leap_years = num_cycles * 8

        remaining_years = (jy - 1) % 33
        for i in range(1, remaining_years + 1):
            if is_jalali_leap(i):
                leap_years += 1

    days_in_month = 0

    if 1 < jm <= 7:
        days_in_month = (jm - 1) * 31

    elif jm > 7:
        days_in_month = 6 * 31 + (jm - 7) * 30
        
    total_days = days_in_year + leap_years + days_in_month + jd - 1
    return JALALI_EPOCH_JDN + total_days

def jdn_to_jalali(jdn: int) -> tuple[int, int, int]:
    """Converts a Julian Day Number to its Jalali date."""
    days_since_epoch = jdn - JALALI_EPOCH_JDN

    num_33_year_cycles = days_since_epoch // 12053
    jy = num_33_year_cycles * 33 + 1
    days_since_epoch %= 12053

    while True:
        days_in_year = 366 if is_jalali_leap(jy) else 365
        if days_since_epoch < days_in_year:
            break
        days_since_epoch -= days_in_year
        jy += 1

    day_of_year = days_since_epoch + 1
    
    if day_of_year <= 186:
        jm = (day_of_year - 1) // 31 + 1
        jd = (day_of_year - 1) % 31 + 1
    else:
        remaining_days = day_of_year - 186
        jm = (remaining_days - 1) // 30 + 7
        jd = (remaining_days - 1) % 30 + 1
        
    return jy, jm, jd

def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """
    Converts a Gregorian date (year, month, day) to a Jalali date.
    
    Returns:
        tuple[int, int, int]: A tuple containing (jalali_year, jalali_month, jalali_day).
    """
    jdn = gregorian_to_jdn(gy, gm, gd)
    return jdn_to_jalali(jdn)

def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
    """
    Converts a Jalali date (year, month, day) to a Gregorian date.
    
    Returns:
        tuple[int, int, int]: A tuple containing (gregorian_year, gregorian_month, gregorian_day).
    """
    jdn = jalali_to_jdn(jy, jm, jd)
    return jdn_to_gregorian(jdn)