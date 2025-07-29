"""Imperial Occasions Dictionary
=============================

Contains mappings of imperial calendar dates to culturally significant 
ancient Persian celebrations and commemorative occasions.

This dictionary is structured by month and day, enabling access to
events in both Persian (FA) and English (EN).
These events are drawn from pre-Islamic Zoroastrian and imperial 
traditions, including Nowruz, Sadeh, Mehregan, and other seasonal
festivals aligned with the ancient Aryan worldview.

Format:
-------
IMPERIAL_OCCASIONS = {
    <month_number>: {
        <day_number>: (
            "<Persian Name> - <Persian Description>",
            "<English Name> - <English Description>"
        ),
        ...
    },
    ...
}

Example:
--------
>>> IMPERIAL_OCCASIONS[1][1]
(".نوروز - آغاز سال نوی شاهنشاهی", "Nowruz - Persian Imperial New Year.",),
>>> IMPERIAL_OCCASIONS[1][1][1].split('-')[0]
Nowruz
"""

IMPERIAL_OCCASIONS: dict[int, dict[int, tuple[str, str]]] = {
    1: {
        1: (
            ".نوروز -آغاز سال نوی شاهنشاهی",
            "Nowruz -Persian Imperial New Year.",
        ),
        3: (
            ".جشن رپیتون -بزرگداشت اوج نور و گرمای روز و نماد پیروزی روشنایی",
            "Rapitton Celebration -Honouring The Zenith of Sunlight, Symbolizing Light's Victory."
        ),
        6: (
            ".خردادروز(نوروز بزرگ) -زادروز زرتشت", 
            "Khordad Day(Great Nowruz) -Birthday of Zoroaster.",
        ),
        10: (
            ".جشن آبانگان -ستایش آناهیتا، ایزدبانوی آب‌های روان",
            "Abangan Celebration -Honouring Anahita, Yazata of Flowing Waters.",
        ),
        13: (
            ".سیزده‌به‌در -پایان جشن نوروز", 
            "Sizdah Bedar -End of Nowruz.",
        ),
        17: (
            "سروش روز -پاسداشت سروش، ایزد پیام‌آور خرد و فرمانبرداری.",
            "Sraosha Day -Honouring Sraosha, The Divine Messenger of Wisdom and Obedience.",
        ),
        19: (
            "فروردینگان -جشن یادبود درگذشتگان.",
            "Farvardingan -Ceremony to Remember The Deceased.",
        ),
    },
    2: {
        2: (
            "اردیبهشتگان -جشن آتش و گلستان.", 
            "Ordibeheshtgan -Festival of Fire and Flowers.",
        ),
        14: (
            "گاهنبار -گاهنبار آفرینش آسمان.",
            "Gahambar -Gahambar of The Heavens Creation.",
        ),
    },
    3: {
        6: (
            "خردادگان -پاسداشت آب و آبادانی", 
            "Khordadgan -Honouring Water and Prosperity.",
        ),
    },
    4: {
        1: (
            ".چله تموز -چله تابستان.",
            "Temouz -Summer Solstice Celebration.",
        ),
        6: (
            "جشن نوپلر -شکوفا شدن گل‌های نیلوفر.",
            "Niloopar Celebration -The Lotus Flowers' Blooming Festival.",
        ),
        12: (
            "گاهنبار -گاهنبار آفرینش آب.",
            "Gahambar -Gahambar of The Waters Creation.",
        ),
        13: (
            "تیرگان -بزرگداشت تیشتر، ستارۀ باران‌آور", 
            "Tirgan -Honouring Tishtrya, The Yazata of Rainfall and Fertility.",
        ),
    },
    5: {
        7: (
            "امردادگان -گرامی‌داشتِ منش و کُنش و خویش‌کاری امُرداد ", 
            "Amordadgan -Honouring Ameretat's Plants, and Purposeful Action; The Yazata of Immortality.",
        ),
    },
    6: {
        4: (
            ".شهریورگان -جشن آتش و بهشت؛ زادروز کوروش بزرگ", 
            "Shahrivargan -Celebration of Fire and Paradise; Birthday of Cyrus The Great.",
        ),
        25: (
            "گاهنبار -گاهنبار آفرینش زمین.",
            "Gahambar -Gahambar of The Earth Creation.",
        ),
    },
    7: {
        1: (
            "مهرگان -نوروز پاییزی.", 
            "Mehregan -Autumnal Nowruz.",
        ),
        10: (
            "مهرگان -نوروز پاییزی.", 
            "Mehregan -Autumnal Nowruz.",
        ),
        16: (
            "مهرگان -نوروز پاییزی؛ آغاز جشن یک هفته‌ای مهرگان", 
            "Mehregan -Autumnal Nowruz; Start of One Week Festival.",
        ),
        17: (
            "مهرگان -نوروز پاییزی؛ جشن یک هفته‌ای مهرگان", 
            "Mehregan -Autumnal Nowruz; One Week Festival.",
        ),
        18: (
            "مهرگان -نوروز پاییزی؛ جشن یک هفته‌ای مهرگان", 
            "Mehregan -Autumnal Nowruz; One Week Festival.",
        ),
        19: (
            "مهرگان -نوروز پاییزی؛ جشن یک هفته‌ای مهرگان", 
            "Mehregan -Autumnal Nowruz; One Week Festival.",
        ),
        20: (
            "مهرگان -نوروز پاییزی؛ جشن یک هفته‌ای مهرگان", 
            "Mehregan -Autumnal Nowruz; One Week Festival.",
        ),
        21: (
            "مهرگان -نوروز پاییزی؛ پایان جشن یک هفته‌ای مهرگان", 
            "Mehregan -Autumnal Nowruz; End of One Week Festival.",
        ),
        24: (
            "گاهنبار -گاهنبار آفرینش گیاهان.",
            "Gahambar -Gahambar of The Plants Creation.",
        ),
    },
    8: {
        10: (
            "آبانگان -ستایش و نیایش ایزدبانوی آب‌های روان، آناهیتا.", 
            "Abangan -Parising Anahita, Yazata of Flowing Waters.",
        ),
    },
    9: {
        9: (
            "آذرگان -جشن گرامیداشت آتش.", 
            "Azargan -Fire Festival in Its Honouring.",
        ),
        30: (
            "شب چله(یلدا) -بلندترین شب سال.",
            "Chelle Night(Yalda Night) -Longest Night of The Year.",
        ),
    },
    10: {
        1: (
            "خرم روز -زادروز خورشید.", 
            "Khorram rooz -Birthday of The Sun.",
        ),
        8: (
            "دیگان نخست -نیایش اهورامزدا.",
            "First Deyegan -Prayers to Ahura Mazda.",
        ),
        14: (
            "گاهنبار -گاهنبار آفرینش جانوران.",
            "Gahambar -Gahambar of The Living Creatures Creation.",
        ),
        15: (
            "بتیکان(دیگان دوم) -جشن ساخت تندیس‌های مردمی ریخت.", 
            "Betikan(Second Deyegan) -Crafting Human-shaped Figurines Festival.",
        ),
        16: (
            "گاوگیل -بازپس‌گیری گاوهای ربوده‌شدۀ پدر فریدون",
            "Gavgil -Reclaiming Stolen Cattles of Feridun's Father.",
        ),
        23: (
            "دیگان سوم -نیایش اهورامزدا.",
            "Third Deyegan -Prayers to Ahura Mazda.",
        ),
    },
    11: {
        2: (
            "بهمنگان -گرامیداشت خرد و اندیشۀ نیک.",
            "Bahmangan -Honouring Wisdom and Good Thoughts.",
        ),
        5: (
            "جشن نوسره -آمادگی برای سده.",
            "Nowsareh -Preparation for The Sadeh Festival.",
        ),
        10: (
            "سده -جشن پیدایش آتش.",
            "Sadeh -Celebration of The Discovery of Fire",
        ),
        22: (
            "جشن کژین(بادروز) -گرامیداشت وای، ایزد باد.",
            "Kazhin(Baad Rooz) -Honouring Vay, The Yazata of Wind.",
        ),
    },
    12: {
        5: (
            "سپندارمذگان -جشن گرامیداشت زن، زمین، زایندگی، و مادر.", 
            "Sepandarmadgan -Honouring Woman, Earth, Fertility, and Mothers.",
        ),

        19: (
            "نوروز انهار -جشن افشاندن عطر و گلاب در آب‌های دشت و دمن.", 
            "Nowruz-e Anhar -Festival of Sprinkling Fragrance and Rosewater in Rivers and Springs."
        ),
        29: (
            "گاهنبار -گاهنبار آفرینش مردمان.",
            "Gahambar -Gahambar of The Man-kind Creation.",
        ),
        30: (
            ".بهیزکی -جشن روز بهیزک",
            "Behizaki -Leap Day Celebration.",
        ),
    },
}
