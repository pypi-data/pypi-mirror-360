"""
Operations with ISO string representing date
Methods can detected by prefix:
dt_ prefixed method results iso_date string (empty string means there was problem)

"""

from datetime import datetime, timedelta

def dt_make(year: int, month: int, day: int) -> str:
    """
    If day is too big then try minimize to end of month. All other errors are errors.
    """
    iso_date = f"{year:04}-{month:02}-{day:02}"
    if is_valid_date(iso_date):
        return iso_date
    else:
        # see põhjustab rekursiooni!!!
        #iso_date = dt_make(year, month, 1)
        #if is_valid_date(iso_date):
        #    return dt_month_end(iso_date)
        return ""

def is_valid_date(iso_date: str) -> bool:
    """
    Checks if argument is really possible ISO date (YYYY-MM-DD)
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return False
    possible = f"{year:04}-{month:02}-{day:02}"
    try:
        _ = datetime.fromisoformat(possible) # this one can emit exception on wrong input
    except:
        return False
    return True

def dt_validate(iso_date: str) -> str:
    """
    Makes input string to regular ISO date if possible (25-9-6 -> 2025-09-06)
    Empty string as result marks error.
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    return dt_make(year, month, day)


def dt_year_start(iso_date: str) -> str:
    """
    Returns first day of year of input date (2025-09-13 -> 2025-01-01)
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    return dt_make(year, 1, 1)

def dt_year_end(iso_date: str) -> str:
    """
    Returns last day of year of input date (2025-09-13 -> 2025-12-31)
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    return dt_make(year, 12, 31)

def dt_month_start(iso_date: str) -> str:
    """
    Returns first day of month of input date (2025-09-13 -> 2025-09-01)
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    return dt_make(year, month, 1)


def dt_from_object(obj: datetime) -> str:
    format = r"%Y-%m-%d"
    return obj.strftime(format)

def int_days_in_month(iso_date: str) -> int:
    """
    Returns number of days in month identified by date
    Solution: take date, find 1st in month (keep), add more then 32 days, find 1st in that month, subtract to find diff in days
    """
    start_of_month = datetime.fromisoformat(dt_month_start(iso_date))
    day_in_next_month = start_of_month + timedelta(days=40)
    start_of_next_month = datetime.fromisoformat(dt_month_start(dt_from_object(day_in_next_month)))
    diff = start_of_next_month - start_of_month
    return diff.days

def dt_month_end(iso_date: str) -> str:
    """
    Returns last day of month of input date (2025-09-13 -> 2025-09-30)
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    day = int_days_in_month(iso_date)
    return dt_make(year, month, day)

# TODO: dt_quarter_start/end, dt_week_start/end (sunday/monday), dt_semiyear_start/end

def is_leap_year(year_or_date: int | str) -> bool:
    if isinstance(year_or_date, int):
        year = year_or_date
    else:
        year, month, day = trio_date(year_or_date)
        if day == 0:
            return False # unclear
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def dt_add_years(iso_date: str, many_years: int, interpret_0228_as_monthend: bool = True) -> str:
    """
    Add full years. If result is 29th february and this is not possible, then return 28th febr
    if flag interpret2802_as_monthend is True then 28th febr becames 29th in leap years
    if False then stays 28th event in leap years
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    go29: bool = False
    if day == 28 and month == 2 and interpret_0228_as_monthend:
        go29 = True
    if day == 29 and month == 2:
        go29 = True
    new_year = year + many_years
    leap_year = is_leap_year(new_year)
    if leap_year and go29:
        new_day = 29
    else:
        new_day = 28
    new_iso_date = dt_make(new_year, month, new_day)
    if not is_valid_date(new_iso_date):
        new_iso_date = dt_make(new_day, month, 28)
    return new_iso_date

def dt_add_months(iso_date: str, many_months: int, stay_in_month_end: bool = True) -> str:
    """
    Add full months. if start and end months have different days in month and start date is end of month try to keep end of month
    """
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    go_end: bool = False
    end_day_1 = int_days_in_month(iso_date)
    if end_day_1 == day and stay_in_month_end:
        go_end = True
    new_month = month + many_months
    new_year = year
    while new_month > 12:
        new_month -= 12
        new_year += 1
    while new_month < 1:
        new_month += 12
        new_year -= 1

    end_day_2 = int_days_in_month(dt_make(new_year, new_month, 1))
    if go_end:
        new_iso_date = dt_make(new_year, new_month, end_day_2)
    else:
        new_day = day
        if new_day > end_day_2:
            new_day = end_day_2
        new_iso_date = dt_make(new_year, new_month, new_day)
    return new_iso_date

def dt_add_days(iso_date: str, many_days: int) -> str:
    year, month, day = trio_date(iso_date)
    if day == 0:
        return ""
    obj_date = datetime.fromisoformat(iso_date)
    new_obj_date = obj_date + timedelta(days=many_days)
    return dt_from_object(new_obj_date)

# TODO: dt_add_quarter, dt_add_semiyear, dt_add_week

# TODO today, compare (dt1, op, d2) => diff(dt1, dt2) in days / months (full/start) / etc
# TODO interacts (periods)

def trio_date(iso_date: str) -> tuple[int, int, int]:
    """
    Helper method to get 3 parts of date delimited by minus, and return tuple. day=0 marks error
    """
    try:
        [year_str, month_str, day_str] = iso_date.split("-", 3) # this one can emit exception on wrong input
        year = int(year_str)
        month = int(month_str)
        day = int(day_str)
        if month > 0 and day > 0:
            return (year, month, day)
        else:
            return (0, 0, 0)
    except:
        return (0, 0, 0)


def tests():
    print("tests..")
    assert dt_make(2025, 2, 28) == "2025-02-28"
    assert is_leap_year(2028) == True
    assert is_leap_year(2000) == True
    assert is_leap_year(1904) == True
    assert is_leap_year(1900) == False

    assert dt_add_years(dt_make(2025, 2, 28), 3) == "2028-02-29"
    assert dt_add_years(dt_make(2025, 2, 28), 3, False) == "2028-02-28"
    assert dt_add_months(dt_make(2025, 3, 29), 1) == "2025-04-29"
    assert dt_add_months(dt_make(2025, 3, 30), 1) == "2025-04-30"
    assert dt_add_months(dt_make(2025, 3, 30), 1, False) == "2025-04-30"
    assert dt_add_months(dt_make(2025, 3, 31), 1) == "2025-04-30"
    assert dt_add_months(dt_make(2025, 3, 31), 1, False) == "2025-04-30"
    assert dt_add_months(dt_make(2025, 3, 29), -1) == "2025-02-28"
    assert dt_add_days(dt_make(2025, 3, 1), 10) == "2025-03-11"
    print("...were fine")

if __name__ == '__main__':
    tests()


