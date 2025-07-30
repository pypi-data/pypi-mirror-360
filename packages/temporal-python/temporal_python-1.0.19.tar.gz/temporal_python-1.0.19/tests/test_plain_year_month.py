"""
Tests for PlainYearMonth class.
"""

import pytest

from temporal import Duration, PlainDate, PlainYearMonth
from temporal.exceptions import InvalidArgumentError, RangeError


class TestPlainYearMonth:
    def test_constructor(self):
        """Test PlainYearMonth constructor."""
        ym = PlainYearMonth(2023, 6)
        assert ym.year == 2023
        assert ym.month == 6
        assert ym.month_code == "M06"
        assert ym.calendar_id == "iso8601"

    def test_properties(self):
        """Test PlainYearMonth properties."""
        ym = PlainYearMonth(2024, 2)  # Leap year February
        assert ym.days_in_month == 29
        assert ym.in_leap_year is True

        ym_non_leap = PlainYearMonth(2023, 2)  # Non-leap year February
        assert ym_non_leap.days_in_month == 28
        assert ym_non_leap.in_leap_year is False

        ym_april = PlainYearMonth(2023, 4)
        assert ym_april.days_in_month == 30

    def test_from_string(self):
        """Test creating PlainYearMonth from string."""
        ym = PlainYearMonth.from_string("2023-06")
        assert ym.year == 2023
        assert ym.month == 6

        with pytest.raises(RangeError):
            PlainYearMonth.from_string("2023-13")  # Invalid month

        with pytest.raises(InvalidArgumentError):
            PlainYearMonth.from_string("invalid")

    def test_add_duration(self):
        """Test adding duration to PlainYearMonth."""
        ym = PlainYearMonth(2023, 6)

        # Add months
        result = ym.add(Duration(months=3))
        assert result.year == 2023
        assert result.month == 9

        # Add years
        result = ym.add(Duration(years=1))
        assert result.year == 2024
        assert result.month == 6

        # Add months with year overflow
        result = ym.add(Duration(months=8))
        assert result.year == 2024
        assert result.month == 2

        # Cannot add time units
        with pytest.raises(InvalidArgumentError):
            ym.add(Duration(days=1))

    def test_subtract(self):
        """Test subtracting from PlainYearMonth."""
        ym1 = PlainYearMonth(2023, 6)
        ym2 = PlainYearMonth(2023, 3)

        # Subtract PlainYearMonth
        duration = ym1.subtract(ym2)
        assert duration.years == 0
        assert duration.months == 3

        # Subtract duration
        result = ym1.subtract(Duration(months=2))
        assert result.year == 2023
        assert result.month == 4

    def test_until_since(self):
        """Test until and since methods."""
        ym1 = PlainYearMonth(2023, 6)
        ym2 = PlainYearMonth(2024, 2)

        duration = ym1.until(ym2)
        assert duration.years == 0
        assert duration.months == 8

        duration_reverse = ym2.since(ym1)
        assert duration_reverse.years == 0
        assert duration_reverse.months == 8

    def test_with_fields(self):
        """Test with_fields method."""
        ym = PlainYearMonth(2023, 6)

        new_ym = ym.with_fields(year=2024)
        assert new_ym.year == 2024
        assert new_ym.month == 6

        new_ym = ym.with_fields(month=12)
        assert new_ym.year == 2023
        assert new_ym.month == 12

    def test_to_plain_date(self):
        """Test converting to PlainDate."""
        ym = PlainYearMonth(2023, 6)
        date = ym.to_plain_date(15)

        assert isinstance(date, PlainDate)
        assert date.year == 2023
        assert date.month == 6
        assert date.day == 15

    def test_comparison(self):
        """Test comparison operators."""
        ym1 = PlainYearMonth(2023, 6)
        ym2 = PlainYearMonth(2023, 8)
        ym3 = PlainYearMonth(2024, 6)
        ym4 = PlainYearMonth(2023, 6)  # Same as ym1

        assert ym1 < ym2
        assert ym1 < ym3
        assert ym2 < ym3
        assert ym1 == ym4
        assert ym2 > ym1
        assert ym3 >= ym1
        assert ym1 <= ym4

    def test_equals(self):
        """Test equals method."""
        ym1 = PlainYearMonth(2023, 6)
        ym2 = PlainYearMonth(2023, 6)
        ym3 = PlainYearMonth(2023, 7)

        assert ym1.equals(ym2)
        assert not ym1.equals(ym3)

    def test_string_representation(self):
        """Test string representations."""
        ym = PlainYearMonth(2023, 6)
        assert str(ym) == "2023-06"
        assert ym.to_json() == "2023-06"
        assert "PlainYearMonth(2023, 6" in repr(ym)

    def test_compare_static(self):
        """Test static compare method."""
        ym1 = PlainYearMonth(2023, 6)
        ym2 = PlainYearMonth(2023, 8)
        ym3 = PlainYearMonth(2023, 6)

        assert PlainYearMonth.compare(ym1, ym2) == -1
        assert PlainYearMonth.compare(ym2, ym1) == 1
        assert PlainYearMonth.compare(ym1, ym3) == 0

    def test_from_any(self):
        """Test from_any class method."""
        ym_original = PlainYearMonth(2023, 6)

        # From PlainYearMonth
        ym1 = PlainYearMonth.from_any(ym_original)
        assert ym1 is ym_original

        # From string
        ym2 = PlainYearMonth.from_any("2023-06")
        assert ym2.year == 2023
        assert ym2.month == 6

        # From dict
        ym3 = PlainYearMonth.from_any({"year": 2023, "month": 6})
        assert ym3.year == 2023
        assert ym3.month == 6

        with pytest.raises(InvalidArgumentError):
            PlainYearMonth.from_any(123)
