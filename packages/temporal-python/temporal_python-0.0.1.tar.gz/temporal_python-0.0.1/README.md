# Temporal Python

A Python port of JavaScript's Temporal API for modern date and time handling.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-75%20passing-brightgreen.svg)

## Overview

The Temporal API provides a modern approach to working with dates and times in Python, offering a more intuitive and reliable alternative to the standard `datetime` module. This library implements the core concepts from the JavaScript Temporal proposal, adapted for Python conventions.

## Features

- **Core Temporal Objects**: PlainDate, PlainTime, PlainDateTime, ZonedDateTime
- **Duration and Instant**: Classes with arithmetic operations
- **Calendar System Support**: ISO 8601 calendar system
- **Parsing and Formatting**: ISO 8601 string parsing and formatting
- **Time Zone Handling**: Time zone operations using Python's `zoneinfo`
- **Comparison Operators**: Full comparison support for temporal objects
- **Type Hints**: Complete type hint coverage for better development experience
- **Immutable Objects**: All temporal objects are immutable for thread safety
- **Comprehensive Testing**: 75 tests covering all functionality

## Installation

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
from temporal import PlainDate, PlainTime, PlainDateTime, Duration, TimeZone, ZonedDateTime

# Working with dates
date = PlainDate(2023, 6, 15)
print(f"Date: {date}")  # 2023-06-15
print(f"Day of week: {date.day_of_week}")  # 4 (Thursday)

# Date arithmetic
future_date = date.add(Duration(days=7))
print(f"One week later: {future_date}")  # 2023-06-22

# Working with times
time = PlainTime(14, 30, 45)
print(f"Time: {time}")  # 14:30:45

# Working with date-times
dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
print(f"DateTime: {dt}")  # 2023-06-15T14:30:45

# Working with timezones
tz = TimeZone("UTC")
zdt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
print(f"Zoned DateTime: {zdt}")  # 2023-06-15T14:30:45Z

# Duration calculations
duration = Duration(days=1, hours=2, minutes=30)
new_dt = dt.add(duration)
print(f"After adding duration: {new_dt}")  # 2023-06-16T17:00:45
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

All 75 tests should pass, covering:
- Core functionality of all temporal classes
- Arithmetic operations and edge cases
- String parsing and formatting
- Timezone handling
- Error conditions and validation

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This library is inspired by the [JavaScript Temporal API proposal](https://tc39.es/proposal-temporal/), adapting its concepts and design patterns for Python while maintaining compatibility with Python conventions and the standard library.
