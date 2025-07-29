"""Imperial Date and Time
=======================
A date and time module based on the Imperial (Shahanshahi) calendar system.

This calendar adds 1180 years to the Jalali (Persian) calendar, aligning it 
with the ancient imperial chronology of Iran, often used by monarchists and
cultural historians to reflect continuity from the foundation of the Persian Empire.

Features:
- Support for Imperial dates and datetimes.
- Conversion to and from Gregorian dates.
- Custom strftime handling with adjusted imperial year.
- (Planned) Day name localization and cultural event recognition.

@Author: Morteza Shoeibi (mortezashoeibi77@gmail.com)

@Version: First stable draft - 2584/04/08 (corresponds to 2025/06/29)

Licensing:
--------
Imperial (Shahanshahi) Calendar Module
Copyright (c) 2025 Morteza Shoeibi <mortezashoeibi77@gmail.com>
Licensed under the Python Software Foundation License.

This module depends on jdatetime:
jdatetime is (c) 2010-2018 Milad Rastian <eslashmili at gmail.com>.
Licensed under the Python Software Foundation License.
See https://docs.python.org/3/license.html for details.

Usage:
------
Import `ImperialDate` and `ImperialDateTime` to work with dates in the
Shahanshahi (Persian Imperial) calendar system.

Example:
--------
>>> from shahanshahi_calendar import ImperialDate
>>> date = ImperialDate.today()
>>> print(date)  # 2584-04-08 
"""



VERSION = "0.1.2"

# Third party modules
import jdatetime

# Python builtin modules
from typing import Union, Any
import datetime
from datetime import date

# Local modules
from shahanshahi_calendar.day_names import IMPERIAL_DAY_NAMES
from shahanshahi_calendar.occasions import IMPERIAL_OCCASIONS



class ImperialDate:
    def __init__(self, year, month, day, locale=None):
        # TODO: Apply a better solution to handle this and support dates before 1180.
        # Handle year complexity in out of range cases
        if year <= 1180: 
            raise ValueError(f"Imperial year must be at least {1181}, got {year}")
        # Internally store Jalali date (Imperial year minus 1180)
        self._jalali_date = jdatetime.date(year - 1180, month, day, locale=locale)
    
    @property
    def year(self) -> int:
        return self._jalali_date.year + 1180

    @property
    def month(self) -> int:
        return self._jalali_date.month

    @property
    def day(self) -> int:
        return self._jalali_date.day

    @property
    def weekday(self) -> int:
        return self._jalali_date.weekday()

    @property
    def locale(self) -> Union[Any, None]:
        return self._jalali_date.locale
    
    @property
    def day_name_fa(self) -> str:
        """Returns the Persian name of the day in the Imperial calendar.
        Leap day is handled separately.
        """
        if self.isleap() and self.month == 12 and self.day == 30:
            return IMPERIAL_DAY_NAMES.get("leap", ("نام‌ناشناس", ""))[0]
        return IMPERIAL_DAY_NAMES.get(self.day, ("نام‌ناشناس", ""))[0]

    @property
    def day_name_en(self) -> str:
        """Returns the English name of the day in the Imperial calendar.
        Leap day is handled separately.
        """
        if self.isleap() and self.month == 12 and self.day == 30:
            return IMPERIAL_DAY_NAMES.get("leap", ("", "Unknown"))[1]
        return IMPERIAL_DAY_NAMES.get(self.day, ("", "Unknown"))[1]
    
    @property
    def occasions_fa(self) -> str:
        """Returns the Persian name of the cultural occasion for this date, if any.
        """
        title = IMPERIAL_OCCASIONS[self.month].get(self.day, ("مناسبتی ندارد.", ""))[0].split('-')[0]
        description = IMPERIAL_OCCASIONS[self.month].get(self.day, ("مناسبتی ندارد.", ""))[0].split('-')[1]
        return {
            'title': title,
            'description': description,
        }

    @property
    def occasions_en(self) -> str:
        """Returns the English name of the cultural occasion for this date, if any.
        """
        title = IMPERIAL_OCCASIONS[self.month].get(self.day, ("", "Not an IMPERIAL OCCASIONS."))[1].split('-')[0]
        description = IMPERIAL_OCCASIONS[self.month].get(self.day, ("", "Not an IMPERIAL OCCASIONS."))[1].split('-')[1]
        return {
            'title': title,
            'description': description,
        }

    def day_name(self, locale: str = 'fa') -> str:
        return self.get_day_info(locale=locale)['day_name']

    def occasion_title(self, locale: str = 'fa') -> str:
        return self.get_day_info(locale=locale)['occasion_title']
    
    def occasion_description(self, locale: str = 'fa') -> str:
        return self.get_day_info(locale=locale)['occasion_description']

    def isleap(self) -> bool:
        """Checks if the current Imperial year is a leap year.
        """
        return self.year % 33 in (1, 5, 9, 13, 17, 22, 26, 30,)

    def togregorian(self) -> date:
        """Converts this ImperialDate to a Gregorian date.
        """
        return self._jalali_date.togregorian()

    def strftime(self, fmt: str) -> str:
        """Formats the date using strftime, replacing the Jalali year with the Imperial year.
        """
        result = self._jalali_date.strftime(fmt)
        return result.replace(str(self._jalali_date.year), str(self.year))

    def get_day_info(self, locale: str = "fa") -> dict:
        """Returns day name and occasion name based on locale.
        
        :param locale: Either 'fa' (Persian) or 'en' (English).
        :return: Dictionary with 'day_name', 'occasion_title'
        and 'occasion_description'.
        """
        is_fa = locale == "fa"

        day_name = self.day_name_fa if is_fa else self.day_name_en

        occasion_title = self.occasions_fa['title'] if is_fa else self.occasions_en['title']
        occasion_description = self.occasions_fa['description'] if is_fa else self.occasions_en['description']

        return {
            "day_name": day_name,
            "occasion_title": occasion_title,
            "occasion_description": occasion_description,
        }


    @classmethod
    def fromgregorian(cls, **kwargs) -> 'ImperialDate':
        """Creates an ImperialDate from a Gregorian date.
        """
        jalali = jdatetime.date.fromgregorian(**kwargs)
        return cls(jalali.year + 1180, jalali.month, jalali.day, jalali.locale)

    @classmethod
    def today(cls, locale: Union[str, None] = None) -> 'ImperialDate':
        """Returns today's date in the Imperial calendar.
        """
        jalali = jdatetime.date.today()
        return cls(jalali.year + 1180, jalali.month, jalali.day, jalali.locale)

    def __str__(self) -> str:
        return f"{self.year:04}-{self.month:02}-{self.day:02}"

    def __repr__(self) -> str:
        return f"ImperialDate({self.year}, {self.month}, {self.day})"


class ImperialDateTime:
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        # jdatetime.datetime does NOT support 'locale'
        self._jalali_dt = jdatetime.datetime(
            year - 1180, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
        )

    @property
    def year(self) -> int:
        return self._jalali_dt.year + 1180

    @property
    def month(self) -> int:
        return self._jalali_dt.month

    @property
    def day(self) -> int:
        return self._jalali_dt.day

    @property
    def hour(self) -> int:
        return self._jalali_dt.hour

    @property
    def minute(self) -> int:
        return self._jalali_dt.minute

    @property
    def second(self) -> int:
        return self._jalali_dt.second

    @property
    def microsecond(self) -> int:
        return self._jalali_dt.microsecond

    @property
    def tzinfo(self) -> Union[Any, None]:
        return self._jalali_dt.tzinfo

    def togregorian(self) -> datetime:
        """Converts this ImperialDateTime to a Gregorian datetime.
        """
        return self._jalali_dt.togregorian()

    def strftime(self, fmt: str) -> str:
        """Formats the datetime using strftime, replacing the Jalali year with the Imperial year.
        """
        result = self._jalali_dt.strftime(fmt)
        return result.replace(str(self._jalali_dt.year), str(self.year))

    @classmethod
    def fromgregorian(cls, **kwargs) -> 'ImperialDateTime':
        """Creates an ImperialDateTime from a Gregorian datetime.
        """
        jalali = jdatetime.datetime.fromgregorian(**kwargs)
        return cls(
            jalali.year + 1180, jalali.month, jalali.day,
            jalali.hour, jalali.minute, jalali.second,
            jalali.microsecond, jalali.tzinfo
        )

    @classmethod
    def now(cls, tz=None) -> 'ImperialDateTime':
        """Returns the current datetime in the Imperial calendar.
        """
        jalali = jdatetime.datetime.now(tz)
        return cls(
            jalali.year + 1180, jalali.month, jalali.day,
            jalali.hour, jalali.minute, jalali.second,
            jalali.microsecond, jalali.tzinfo
        )

    def __str__(self) -> str:
        return f"{self.year:04}-{self.month:02}-{self.day:02} {self.hour:02}:{self.minute:02}:{self.second:02}"

    def __repr__(self) -> str:
        return (
            f"ImperialDateTime({self.year}, {self.month}, {self.day}, "
            f"{self.hour}, {self.minute}, {self.second}, {self.microsecond})"
        )
