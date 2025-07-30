"""
Tests for PlainDate class.
"""

import unittest

from temporal import Calendar, Duration, PlainDate
from temporal.exceptions import InvalidArgumentError, RangeError


class TestPlainDate(unittest.TestCase):
    def test_constructor(self):
        """Test PlainDate constructor."""
        date = PlainDate(2023, 6, 15)
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 15)

    def test_constructor_with_calendar(self):
        """Test PlainDate constructor with calendar."""
        calendar = Calendar("iso8601")
        date = PlainDate(2023, 6, 15, calendar)
        self.assertEqual(date.calendar, calendar)

    def test_invalid_date(self):
        """Test invalid date values."""
        with self.assertRaises(RangeError):
            PlainDate(2023, 13, 15)  # Invalid month

        with self.assertRaises(RangeError):
            PlainDate(2023, 2, 30)  # Invalid day for February

    def test_day_of_week(self):
        """Test day of week calculation."""
        date = PlainDate(2023, 6, 15)  # Thursday
        self.assertEqual(date.day_of_week, 4)

    def test_day_of_year(self):
        """Test day of year calculation."""
        date = PlainDate(2023, 6, 15)
        self.assertEqual(date.day_of_year, 166)

    def test_add_duration(self):
        """Test adding duration to date."""
        date = PlainDate(2023, 6, 15)
        duration = Duration(days=10)
        new_date = date.add(duration)
        self.assertEqual(new_date.day, 25)

    def test_subtract_duration(self):
        """Test subtracting duration from date."""
        date = PlainDate(2023, 6, 15)
        duration = Duration(days=5)
        new_date = date.subtract(duration)
        self.assertEqual(new_date.day, 10)

    def test_subtract_date(self):
        """Test subtracting date from date."""
        date1 = PlainDate(2023, 6, 20)
        date2 = PlainDate(2023, 6, 15)
        duration = date1.subtract(date2)
        self.assertEqual(duration.days, 5)

    def test_with_fields(self):
        """Test with_fields method."""
        date = PlainDate(2023, 6, 15)
        new_date = date.with_fields(year=2024, day=20)
        self.assertEqual(new_date.year, 2024)
        self.assertEqual(new_date.month, 6)
        self.assertEqual(new_date.day, 20)

    def test_comparison(self):
        """Test date comparison."""
        date1 = PlainDate(2023, 6, 15)
        date2 = PlainDate(2023, 6, 20)
        date3 = PlainDate(2023, 6, 15)

        self.assertLess(date1, date2)
        self.assertGreater(date2, date1)
        self.assertEqual(date1, date3)
        self.assertLessEqual(date1, date3)
        self.assertGreaterEqual(date1, date3)

    def test_string_representation(self):
        """Test string representation."""
        date = PlainDate(2023, 6, 15)
        self.assertEqual(str(date), "2023-06-15")

    def test_from_string(self):
        """Test creating date from string."""
        date = PlainDate.from_string("2023-06-15")
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 15)

    def test_today(self):
        """Test today method."""
        today = PlainDate.today()
        self.assertIsInstance(today, PlainDate)
        self.assertGreaterEqual(today.year, 2023)


if __name__ == "__main__":
    unittest.main()
