import calendar


def get_days_in_month(date, month_adder=0):
    """Find number of days in month for given datetime object."""
    return calendar.monthrange(date.year, date.month + month_adder)[1]
