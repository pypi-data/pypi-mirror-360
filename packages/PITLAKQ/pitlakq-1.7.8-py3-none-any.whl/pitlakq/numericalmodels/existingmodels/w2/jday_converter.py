"""Jdays to dates and back.
"""
from __future__ import print_function

import datetime
import calendar


class JdayConverter(object):
    """Conversion of dates to jdays and back.
    """

    def __init__(self, start):
        self.start = start
        self.jday_start = (datetime.datetime(start.year, 1, 1) -
                           datetime.timedelta(1))

    def make_jday_from_date(self, date):
        """Convert date to jday."""
        delta = date - self.jday_start
        return (delta.days + delta.seconds / 8.64e4 +
                delta.microseconds / 8.64e10)

    def make_date_from_jday(self, jday):
        """Convert jday to date."""
        days, day_fraction = divmod(jday, 1)
        seconds = day_fraction * 8.64e4
        delta = datetime.timedelta(days, seconds)
        return self.jday_start + delta


class JdayConverterComplex(object):
    """Conversion of dates to jdays and back.
       A much more complex version. Not needed anymore
       except for testing.

       Jdays are counted continously through the years.
       In the first year they are identical to the
       day_of_year. In the following year the will be
       day_of_year plus the days of the previous years.
       Finest resolution is milliseconds, i.e 1000er steps
       for microseconds in datetiemmake_cumulative_days_in_years.datetime
       instances.
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self._cum_days_in_month_normal = [0, 31, 59, 90, 120, 151, 181, 212,
                                          243, 273, 304, 334, 365]
        self._cum_days_in_month_leap_year = [0, 31, 60, 91, 121, 152, 182, 213,
                                             244, 274, 305, 335, 366]
        self.year_range = range(self.start.year, self.end.year + 1)
        self.changes = {}
        self.lower_than_start = int(-1e8+1)
        self.higher_than_end = int(1e8)
        self.cumulative_days_in_years = []
        self.year_index = {}

    def make_cumulative_days_in_years(self):
        """Calculate cumulative number of days from start to end."""
        cumulated = 0
        for n, year in enumerate(self.year_range):
            self.year_index[year] = n
            if calendar.isleap(year):
                days = 366
            else:
                days = 365
            self.cumulative_days_in_years.append(days + cumulated)
            cumulated = self.cumulative_days_in_years[n]
        self.cumulative_days_in_years = [0] + self.cumulative_days_in_years

    def day_of_year(self, date):
        """Day of year"""
        index = date.month - 1
        if calendar.isleap(date.year):
            prior_month_days = self._cum_days_in_month_leap_year[index]
        else:
            prior_month_days = self._cum_days_in_month_normal[index]
        return date.day + prior_month_days

    def make_jday_from_date(self, date):
        """Convert date to jday."""
        try:
            full_days = (
                self.cumulative_days_in_years[self.year_index[date.year]] +
                self.day_of_year(date))
        except KeyError:
            if date.year < self.start.year:
                return self.lower_than_start
            elif date.year > self.end.year:
                return self.higher_than_end
            else:
                assert False, 'This place should never be reached.'
        day_fraction = (date.hour /24.0 + date.minute / 1440.0 +
                       date.second / 8.64e4 + date.microsecond / 8.64e10)
        return full_days + day_fraction

    def make_date_from_jday(self, jday):
        """Convert jday to date."""
        trial_year = self.year_range[int(jday / 365.25)]
        initial_start_year = trial_year
        trial_index = self.year_index[trial_year]
        max_tries = 1
        tries = 0
        lower_limit = self.cumulative_days_in_years[trial_index] + 1
        upper_limit = self.cumulative_days_in_years[trial_index + 1] + 1
        while True:
            if tries > max_tries:
                print(trial_year, lower_limit, jday, upper_limit, end='')
                print(upper_limit - lower_limit)
                raise OverflowError
            if lower_limit <= jday < upper_limit:
                change = initial_start_year - trial_year
                self.changes.setdefault(change, 0)
                self.changes[change] += 1
                year = trial_year
                break
            else:
                tries += 1
                if jday >= upper_limit:
                    trial_year += 1
                elif jday < lower_limit:
                    trial_year -= 1
                trial_index = self.year_index[trial_year]
                lower_limit = self.cumulative_days_in_years[trial_index] + 1
                upper_limit = (
                    self.cumulative_days_in_years[trial_index + 1] + 1)
        upper_limit = (jday -
                        self.cumulative_days_in_years[self.year_index[year]])
        days_in_year = int(upper_limit)
        month = -999
        if calendar.isleap(year):
            cumulative_days_in_month = self._cum_days_in_month_leap_year
        else:
            cumulative_days_in_month = self._cum_days_in_month_normal
        for month, cumulative_days in enumerate(cumulative_days_in_month):
            if days_in_year <= cumulative_days:
                break
        if month == 1:
            day = days_in_year
        else:
            day = days_in_year - cumulative_days_in_month[month - 1]
        partial_day = upper_limit - days_in_year
        hours_with_fraction = partial_day * 24
        hours = int(round((hours_with_fraction), 4))
        if hours:
            minutes_with_fraction = (hours_with_fraction - hours) * 60
        else:
            minutes_with_fraction = hours_with_fraction * 60
        minutes = int(round(minutes_with_fraction, 2))
        if minutes:
            seconds_with_fraction = (minutes_with_fraction - minutes) * 60
        else:
            seconds_with_fraction = minutes_with_fraction * 60
        seconds = int(round(seconds_with_fraction, 2))
        if seconds:
            microseconds_with_fraction = (
                (seconds_with_fraction - seconds) * 1e6)
        else:
            microseconds_with_fraction = seconds_with_fraction * 1e6
        microseconds = int(round(microseconds_with_fraction, -3))
        return datetime.datetime(year, month, day, hours, minutes, seconds,
                                 microseconds)
