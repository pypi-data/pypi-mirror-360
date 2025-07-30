# Temporal Python

A complete Python port of JavaScript's Temporal API for modern date and time handling.

[![CI](https://github.com/hasanatkazmi/temporal-python/workflows/CI/badge.svg)](https://github.com/hasanatkazmi/temporal-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/hasanatkazmi/temporal-python/branch/main/graph/badge.svg)](https://codecov.io/gh/hasanatkazmi/temporal-python)
[![PyPI version](https://badge.fury.io/py/temporal-python.svg)](https://badge.fury.io/py/temporal-python)
[![Python Support](https://img.shields.io/pypi/pyversions/temporal-python.svg)](https://pypi.org/project/temporal-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Tests](https://img.shields.io/badge/tests-101%20passing-brightgreen.svg)](#testing)

## Overview

The Temporal API provides a modern approach to working with dates and times in Python, offering a more intuitive and reliable alternative to the standard `datetime` module. This library implements the core concepts from the JavaScript Temporal proposal, adapted for Python conventions.

## Features

- **Complete Temporal Objects**: PlainDate, PlainTime, PlainDateTime, PlainYearMonth, PlainMonthDay, ZonedDateTime
- **Duration and Instant**: Classes with arithmetic operations and advanced methods
- **Calendar System Support**: ISO 8601 calendar system with extensible architecture
- **Parsing and Formatting**: Complete ISO 8601 string parsing and formatting
- **Time Zone Handling**: Full timezone operations using Python's `zoneinfo`
- **Advanced Methods**: until(), since(), round(), compare(), total() and more
- **Flexible Input**: from_any() methods support multiple input types
- **Comparison Operators**: Full comparison support for all temporal objects
- **Type Hints**: Complete type hint coverage for better development experience
- **Immutable Objects**: All temporal objects are immutable for thread safety
- **Comprehensive Testing**: 101 tests covering all functionality including new classes

## Installation

### From PyPI

```bash
pip install temporal-python
```

### From Source

```bash
git clone https://github.com/hasanatkazmi/temporal-python.git
cd temporal-python
pip install -e .
```

### Requirements

- Python 3.7+
- `zoneinfo` (included in Python 3.9+, or install `backports.zoneinfo` for older versions)

## Quick Start

```python
from temporal import (PlainDate, PlainTime, PlainDateTime, PlainYearMonth,
                     PlainMonthDay, Duration, TimeZone, ZonedDateTime, Instant)

# Working with dates
date = PlainDate(2023, 6, 15)
print(f"Date: {date}")  # 2023-06-15
print(f"Day of week: {date.day_of_week}")  # 4 (Thursday)

# Date arithmetic and advanced methods
future_date = date.add(Duration(days=7))
print(f"One week later: {future_date}")  # 2023-06-22
duration_between = date.until(future_date)
print(f"Duration: {duration_between}")  # P7D

# Working with year-month combinations
year_month = PlainYearMonth(2023, 6)
print(f"Year-Month: {year_month}")  # 2023-06
print(f"Days in month: {year_month.days_in_month}")  # 30

# Working with recurring dates (birthdays, holidays)
birthday = PlainMonthDay(8, 24)
print(f"Birthday: {birthday}")  # --08-24
print(f"Valid in 2024: {birthday.is_valid_for_year(2024)}")  # True

# Working with times and rounding
time = PlainTime(14, 30, 45, 123456)
print(f"Time: {time}")  # 14:30:45.123456
rounded_time = time.round('seconds')
print(f"Rounded: {rounded_time}")  # 14:30:45

# Working with date-times
dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
print(f"DateTime: {dt}")  # 2023-06-15T14:30:45

# Working with timezones
tz = TimeZone("UTC")
zdt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
print(f"Zoned DateTime: {zdt}")  # 2023-06-15T14:30:45Z
print(f"Start of day: {zdt.start_of_day()}")  # 2023-06-15T00:00:00Z

# Duration calculations with advanced methods
duration = Duration(days=1, hours=2, minutes=30)
print(f"Total hours: {duration.total('hours')}")  # 26.5
rounded_duration = duration.round('hours')
print(f"Rounded duration: {rounded_duration}")  # P1DT3H

# Working with instants (exact moments in time)
instant = Instant.now()
future_instant = instant.add(Duration(hours=1))
time_diff = instant.until(future_instant)
print(f"Time difference: {time_diff}")  # PT1H

# Flexible input with from_any methods
date_from_string = PlainDate.from_any("2023-06-15")
date_from_dict = PlainDate.from_any({"year": 2023, "month": 6, "day": 15})
print(f"Same date: {date_from_string == date_from_dict}")  # True
```

## Core Classes

### PlainDate
Represents a calendar date without time or timezone information.

```python
date = PlainDate(2023, 6, 15)
date = PlainDate.from_string("2023-06-15")
date = PlainDate.today()
```

### PlainTime
Represents a time-of-day without date or timezone information.

```python
time = PlainTime(14, 30, 45, 123456)  # hour, minute, second, microsecond
time = PlainTime.from_string("14:30:45.123456")
```

### PlainDateTime
Represents a date and time without timezone information.

```python
dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
dt = PlainDateTime.from_string("2023-06-15T14:30:45")
dt = PlainDateTime.now()
```

### PlainYearMonth
Represents a year-month combination without a specific day.

```python
ym = PlainYearMonth(2023, 6)
ym = PlainYearMonth.from_string("2023-06")
print(ym.days_in_month)  # 30
print(ym.in_leap_year)   # False
```

### PlainMonthDay
Represents a month-day combination without a year (useful for recurring dates).

```python
md = PlainMonthDay(8, 24)  # August 24th
md = PlainMonthDay.from_string("--08-24")
feb29 = PlainMonthDay(2, 29)
print(feb29.is_valid_for_year(2024))  # True (leap year)
print(feb29.is_valid_for_year(2023))  # False (not leap year)
```

### ZonedDateTime
Represents a date and time with timezone information.

```python
tz = TimeZone("UTC")
zdt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
zdt = ZonedDateTime.now(tz)
```

### Duration
Represents a duration of time with support for various units.

```python
duration = Duration(days=1, hours=2, minutes=30, seconds=45)
duration = Duration.from_string("P1DT2H30M45S")  # ISO 8601 format
```

### Instant
Represents an exact point in time (Unix timestamp).

```python
instant = Instant.now()
instant = Instant.from_epoch_seconds(1687438245)
instant = Instant.from_string("2023-06-22T12:50:45Z")
```

## Operations

### Arithmetic
All temporal objects support arithmetic operations:

```python
# Adding/subtracting durations
new_date = date.add(Duration(days=7))
new_time = time.subtract(Duration(hours=1))

# Subtracting temporal objects returns durations
diff = date2.subtract(date1)  # Returns Duration
```

### Comparisons
All temporal objects support comparison operations:

```python
date1 < date2
time1 >= time2
dt1 == dt2
```

### Conversions
Convert between different temporal types:

```python
# Extract components
date_part = dt.to_plain_date()
time_part = dt.to_plain_time()

# Add timezone information
zdt = dt.to_zoned_date_time(timezone)

# Convert to instant
instant = zdt.to_instant()
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

All 101 tests should pass, covering:
- Core functionality of all temporal classes (including PlainYearMonth and PlainMonthDay)
- Arithmetic operations and edge cases
- Advanced methods like until(), since(), round(), and total()
- String parsing and formatting for all classes
- Timezone handling and disambiguation
- Static comparison methods and flexible input handling
- Error conditions and comprehensive validation

## Examples

See `example.py` for comprehensive usage examples including:
- Basic date/time operations
- Duration arithmetic
- Timezone conversions
- Business day calculations
- Error handling

```bash
python example.py
```

## API Reference

### Error Handling

The library defines custom exceptions:

- `TemporalError`: Base exception for all temporal errors
- `RangeError`: Value outside valid range
- `InvalidArgumentError`: Invalid argument provided
- `TemporalTypeError`: Inappropriate type for operation

### ISO 8601 Support

Full support for ISO 8601 parsing and formatting:

```python
# Dates: YYYY-MM-DD
PlainDate.from_string("2023-06-15")

# Times: HH:MM:SS[.ffffff]
PlainTime.from_string("14:30:45.123456")

# DateTimes: YYYY-MM-DDTHH:MM:SS[.ffffff]
PlainDateTime.from_string("2023-06-15T14:30:45")

# Durations: P[nY][nM][nW][nD][T[nH][nM][nS]]
Duration.from_string("P1DT2H30M45S")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Automatic Versioning

This project uses automatic semantic versioning:
- **Patch** bumps (bug fixes) happen automatically on every merge to main
- **Minor** bumps (new features) use `feat:` commits or `version:minor` PR labels
- **Major** bumps (breaking changes) use `BREAKING CHANGE:` commits or `version:major` PR labels
- Skip versioning with `[skip version]` in commits or `no-version-bump` PR labels

See [.github/VERSIONING.md](.github/VERSIONING.md) for complete details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This library is inspired by the [JavaScript Temporal API proposal](https://tc39.es/proposal-temporal/), adapting its concepts and design patterns for Python while maintaining compatibility with Python conventions and the standard library.
