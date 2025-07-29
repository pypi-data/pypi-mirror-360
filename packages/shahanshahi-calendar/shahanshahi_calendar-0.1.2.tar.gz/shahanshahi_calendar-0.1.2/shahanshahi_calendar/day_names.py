"""Imperial Day Names Dictionary
=============================

Provides the traditional names assigned to each day of the month
in the Imperial (Shahanshahi) calendar system, consistent with
Zoroastrian practice.
Each day of every month carries a unique spiritual or divine name
in the Zoroastrian tradition—many of which are deities or elements
of nature— and is preserved here for localization and cultural 
reflection.

Format:
-------
IMPERIAL_DAY_NAMES = {
    <day_number>: ("<Persian Name>", "<English Name>"),
    ...
    "leap": ("<Persian Leap Day Name>", "<English Leap Day Name>")
}

Example:
--------
>>> IMPERIAL_DAY_NAMES[6]
("خرداد", "Khordad")
"""
from typing import Any

IMPERIAL_DAY_NAMES: dict[Any, tuple[str, str]] = {
    1: ("هورمزد", "Hormozd"),
    2: ("بهمن", "Bahman"),
    3: ("اردیبهشت", "Ordibehesht"),
    4: ("شهریور", "Shahrivar"),
    5: ("سپندارمذ", "Sepandarmad"),
    6: ("خرداد", "Khordad"),
    7: ("امرداد", "Amordad"),
    8: ("دی به آذر", "Dey be Azar"),
    9: ("آذر", "Azar"),
    10: ("آبان", "Aban"),
    11: ("خور", "Khorshid"),
    12: ("ماه", "Mah"),
    13: ("تیر", "Tir"),
    14: ("گوش", "Gosh"),
    15: ("دی به مهر", "Dey be Mehr"),
    16: ("مهر", "Mehr"),
    17: ("سروش", "Soroush"),
    18: ("رشن", "Rashn"),
    19: ("فروردین", "Farvardin"),
    20: ("بهرام", "Bahram"),
    21: ("رام", "Ram"),
    22: ("باد", "Bad"),
    23: ("دی به دین", "Dey be Din"),
    24: ("دین", "Din"),
    25: ("ارد", "Ard"),
    26: ("اشتاد", "Eshtad"),
    27: ("آسمان", "Asman"),
    28: ("زامیاد", "Zamyad"),
    29: ("مانتره‌سپند", "Manthra Spenta"),
    30: ("انارام", "Anaram"),
    31: ("اورداد/زُروان", "Ordad/Zurvan"),
    "leap": ("اورداد", "Ordad"),
}
