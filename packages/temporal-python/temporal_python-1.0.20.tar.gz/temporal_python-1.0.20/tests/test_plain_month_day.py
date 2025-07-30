"""
Tests for PlainMonthDay class.
"""

import pytest

from temporal import PlainDate, PlainMonthDay
from temporal.exceptions import InvalidArgumentError, RangeError


class TestPlainMonthDay:
    def test_constructor(self):
        """Test PlainMonthDay constructor."""
        md = PlainMonthDay(8, 24)
        assert md.month == 8
        assert md.day == 24
        assert md.month_code == "M08"
        assert md.calendar_id == "iso8601"

    def test_february_29(self):
        """Test February 29 handling."""
        feb29 = PlainMonthDay(2, 29)
        assert feb29.month == 2
        assert feb29.day == 29

        # Should be valid for leap years
        assert feb29.is_valid_for_year(2024)  # Leap year
        assert not feb29.is_valid_for_year(2023)  # Non-leap year

    def test_invalid_dates(self):
        """Test invalid date handling."""
        with pytest.raises(RangeError):
            PlainMonthDay(2, 30)  # February 30 doesn't exist

        with pytest.raises(RangeError):
            PlainMonthDay(4, 31)  # April 31 doesn't exist

        with pytest.raises(RangeError):
            PlainMonthDay(13, 1)  # Month 13 doesn't exist

    def test_from_string(self):
        """Test creating PlainMonthDay from string."""
        md1 = PlainMonthDay.from_string("--08-24")
        assert md1.month == 8
        assert md1.day == 24

        md2 = PlainMonthDay.from_string("08-24")
        assert md2.month == 8
        assert md2.day == 24

        with pytest.raises(InvalidArgumentError):
            PlainMonthDay.from_string("invalid")

    def test_with_fields(self):
        """Test with_fields method."""
        md = PlainMonthDay(8, 24)

        new_md = md.with_fields(month=12)
        assert new_md.month == 12
        assert new_md.day == 24

        new_md = md.with_fields(day=15)
        assert new_md.month == 8
        assert new_md.day == 15

    def test_to_plain_date(self):
        """Test converting to PlainDate."""
        md = PlainMonthDay(8, 24)
        date = md.to_plain_date(2023)

        assert isinstance(date, PlainDate)
        assert date.year == 2023
        assert date.month == 8
        assert date.day == 24

        # Test February 29 in non-leap year
        feb29 = PlainMonthDay(2, 29)
        with pytest.raises(RangeError):
            feb29.to_plain_date(2023)  # 2023 is not a leap year

        # Should work for leap year
        date_leap = feb29.to_plain_date(2024)
        assert date_leap.year == 2024
        assert date_leap.month == 2
        assert date_leap.day == 29

    def test_is_valid_for_year(self):
        """Test is_valid_for_year method."""
        md_normal = PlainMonthDay(8, 24)
        assert md_normal.is_valid_for_year(2023)
        assert md_normal.is_valid_for_year(2024)

        feb29 = PlainMonthDay(2, 29)
        assert not feb29.is_valid_for_year(2023)  # Non-leap year
        assert feb29.is_valid_for_year(2024)  # Leap year
        assert not feb29.is_valid_for_year(1900)  # Non-leap year (divisible by 100)
        assert feb29.is_valid_for_year(2000)  # Leap year (divisible by 400)

    def test_get_valid_year(self):
        """Test get_valid_year method."""
        md_normal = PlainMonthDay(8, 24)
        assert md_normal.get_valid_year(2023) == 2023

        feb29 = PlainMonthDay(2, 29)
        assert feb29.get_valid_year(2024) == 2024  # Already valid

        # Should find next leap year
        valid_year = feb29.get_valid_year(2023)
        assert valid_year >= 2024
        assert feb29.is_valid_for_year(valid_year)

    def test_comparison(self):
        """Test comparison operators."""
        md1 = PlainMonthDay(6, 15)
        md2 = PlainMonthDay(8, 24)
        md3 = PlainMonthDay(6, 20)
        md4 = PlainMonthDay(6, 15)  # Same as md1

        assert md1 < md2
        assert md1 < md3
        assert md2 > md3
        assert md1 == md4
        assert md2 >= md1
        assert md1 <= md4

    def test_equals(self):
        """Test equals method."""
        md1 = PlainMonthDay(8, 24)
        md2 = PlainMonthDay(8, 24)
        md3 = PlainMonthDay(8, 25)

        assert md1.equals(md2)
        assert not md1.equals(md3)

    def test_string_representation(self):
        """Test string representations."""
        md = PlainMonthDay(8, 24)
        assert str(md) == "--08-24"
        assert md.to_json() == "--08-24"
        assert "PlainMonthDay(8, 24" in repr(md)

    def test_compare_static(self):
        """Test static compare method."""
        md1 = PlainMonthDay(6, 15)
        md2 = PlainMonthDay(8, 24)
        md3 = PlainMonthDay(6, 15)

        assert PlainMonthDay.compare(md1, md2) == -1
        assert PlainMonthDay.compare(md2, md1) == 1
        assert PlainMonthDay.compare(md1, md3) == 0

    def test_from_any(self):
        """Test from_any class method."""
        md_original = PlainMonthDay(8, 24)

        # From PlainMonthDay
        md1 = PlainMonthDay.from_any(md_original)
        assert md1 is md_original

        # From string
        md2 = PlainMonthDay.from_any("--08-24")
        assert md2.month == 8
        assert md2.day == 24

        # From dict
        md3 = PlainMonthDay.from_any({"month": 8, "day": 24})
        assert md3.month == 8
        assert md3.day == 24

        with pytest.raises(InvalidArgumentError):
            PlainMonthDay.from_any(123)
