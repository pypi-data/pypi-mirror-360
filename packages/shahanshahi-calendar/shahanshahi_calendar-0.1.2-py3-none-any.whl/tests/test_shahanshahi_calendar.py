"""test_shahanshahi_calendar.py

This module contains unit tests for the `ImperialDate` and `ImperialDate` classes,
which implements date functionality based on the Imperial Iranian calendar system.

Tests cover:
- Leap year calculations (`isleap`).
- Day and month validations.
- Date conversions and internal representations.
- Human-readable information (e.g., day names, occasions).
- Locale-based formatting in both Persian ("fa") and English ("en").
"""

import pytest
import datetime
from shahanshahi_calendar import ImperialDate, ImperialDateTime

def test_imperial_date_creation():
    date = ImperialDate(2584, 4, 8)
    assert date.year == 2584
    assert date.month == 4
    assert date.day == 8

def test_imperial_date_invalid_year():
    with pytest.raises(ValueError):
        ImperialDate(1000, 1, 1)

def test_isleap_true():
    assert ImperialDate(2583, 1, 1).isleap() is True 

def test_isleap_false():
    assert ImperialDate(2584, 1, 1).isleap() is False

def test_day_name_and_occasion_fa():
    date = ImperialDate(2584, 1, 1)
    info = date.get_day_info(locale="fa")
    assert isinstance(info["day_name"], str)
    assert isinstance(info["occasion"], str)


def test_day_name_and_occasion_en():
    date = ImperialDate(2584, 1, 1)
    info = date.get_day_info(locale="en")
    assert "Unknown" in info["day_name"] or info["day_name"].isalpha()
    assert isinstance(info["occasion"], str)

def test_togregorian_and_fromgregorian():
    g = datetime.date(2025, 6, 30)
    imperial = ImperialDate.fromgregorian(date=g)
    back_to_g = imperial.togregorian()
    assert back_to_g == g

def test_imperial_date_str_and_repr():
    d = ImperialDate(2584, 4, 8)
    assert str(d) == "2584-04-08"
    assert repr(d) == "ImperialDate(2584, 4, 8)"

def test_imperial_datetime_creation_and_properties():
    dt = ImperialDateTime(2584, 4, 8, 12, 30, 45)
    assert dt.year == 2584
    assert dt.month == 4
    assert dt.day == 8
    assert dt.hour == 12
    assert dt.minute == 30
    assert dt.second == 45

def test_imperial_datetime_conversion():
    gdt = datetime.datetime(2025, 6, 30, 14, 15)
    imperial_dt = ImperialDateTime.fromgregorian(datetime=gdt)
    back_to_gdt = imperial_dt.togregorian()
    assert back_to_gdt.year == gdt.year
    assert back_to_gdt.month == gdt.month
    assert back_to_gdt.day == gdt.day
    assert back_to_gdt.hour == gdt.hour
    assert back_to_gdt.minute == gdt.minute

def test_imperial_datetime_str_and_repr():
    dt = ImperialDateTime(2584, 4, 8, 12, 0, 0)
    assert str(dt).startswith("2584-04-08")
    assert "ImperialDateTime(2584, 4, 8" in repr(dt)
