# Shahanshahi Calendar (Imperial Calendar for Python)

A Persian Imperial (Shahanshahi) calendar system based on the Jalali calendar with extended date and time support.

## Features
- Convert between Gregorian and Imperial dates.
- Get current Imperial date and time.
- Supports Persian day names and historical festivals.

## Install
```bash
pip install shahanshahi-calendar
```
## Example
```python
from shahanshahi_calendar import ImperialDate

today = ImperialDate.today()
print(today)  # e.g. 2584-04-09
print(today.day_name_en) # e.g Azar
```

## TODO
- **Enhance year handling for pre-1180 dates**: Develop a fallback mechanism to handle dates before 1180 by treating them as pure Jalali dates or allowing a configurable mode to bypass the Imperial year adjustment.
- **Add locale support to `ImperialDateTime`**: Extend `ImperialDateTime` to support locale settings, aligning with `ImperialDate` for consistent multilingual output (e.g., in `strftime` or occasion names).
- **Optimize `IMPERIAL_DAY_NAMES` and `IMPERIAL_OCCASIONS`**:
  - Move `IMPERIAL_DAY_NAMES` and `IMPERIAL_OCCASIONS` to external JSON/YAML files for easier maintenance, updates, and scalability.
  - Validate and document duplicate entries in `IMPERIAL_OCCASIONS` (e.g., multiple events on the same day, like 3/6 for both "Khordad Day" and "Nilufar Festival").
  - Add support for querying multiple occasions on a single date (e.g., return a list of events instead of a single tuple).
- **Support date arithmetic**: Implement `__add__` and `__sub__` methods for `ImperialDate` and `ImperialDateTime` to support operations with `timedelta`, leveraging `jdatetime` for accuracy.
- **Improve error handling**: Introduce a custom `ImperialDateError` class with user-friendly messages tailored to the Imperial calendar, especially for invalid dates or unsupported locales.
- **Expand cultural event support**:
  - Add validation for `IMPERIAL_OCCASIONS` to ensure all months and key cultural events (e.g., Nowruz, Mehregan) are covered comprehensively.
  - Implement a feature to query events by name or date range (e.g., list all festivals in a given month).
  - Include historical context or descriptions for each occasion in the data structure (e.g., a brief note about the significance of Nowruz or Sadeh).
- **Optimize performance**: Cache frequent year conversions (e.g., adding/subtracting 1180) and optimize lookups in `IMPERIAL_DAY_NAMES` and `IMPERIAL_OCCASIONS` for large-scale usage.
- **Add CLI interface**: Create a command-line tool for quick conversions (e.g., Gregorian to Imperial) and querying day names or occasions (e.g., `imperial_calendar --date 2025-06-30 --occasion`).
- **Enhance documentation**:
  - Add detailed documentation for `IMPERIAL_DAY_NAMES` and `IMPERIAL_OCCASIONS`, including their Zoroastrian origins and usage examples.
  - Provide a clear roadmap for planned features, such as expanded localization and cultural event recognition.
  - Include examples of how to use day names and occasions in both Persian and English contexts.
