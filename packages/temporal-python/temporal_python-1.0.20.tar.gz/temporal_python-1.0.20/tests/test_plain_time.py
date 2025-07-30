"""
Tests for PlainTime class.
"""

import unittest

from temporal import Duration, PlainTime
from temporal.exceptions import InvalidArgumentError, RangeError


class TestPlainTime(unittest.TestCase):
    def test_constructor(self):
        """Test PlainTime constructor."""
        time = PlainTime(14, 30, 45, 123456)
        self.assertEqual(time.hour, 14)
        self.assertEqual(time.minute, 30)
        self.assertEqual(time.second, 45)
        self.assertEqual(time.microsecond, 123456)

    def test_constructor_defaults(self):
        """Test PlainTime constructor with defaults."""
        time = PlainTime()
        self.assertEqual(time.hour, 0)
        self.assertEqual(time.minute, 0)
        self.assertEqual(time.second, 0)
        self.assertEqual(time.microsecond, 0)

    def test_invalid_time(self):
        """Test invalid time values."""
        with self.assertRaises(RangeError):
            PlainTime(25, 0, 0)  # Invalid hour

        with self.assertRaises(RangeError):
            PlainTime(0, 60, 0)  # Invalid minute

        with self.assertRaises(RangeError):
            PlainTime(0, 0, 60)  # Invalid second

    def test_add_duration(self):
        """Test adding duration to time."""
        time = PlainTime(14, 30, 45)
        duration = Duration(hours=2, minutes=15)
        new_time = time.add(duration)
        self.assertEqual(new_time.hour, 16)
        self.assertEqual(new_time.minute, 45)

    def test_add_duration_overflow(self):
        """Test adding duration with overflow."""
        time = PlainTime(22, 30, 0)
        duration = Duration(hours=3)
        new_time = time.add(duration)
        self.assertEqual(new_time.hour, 1)  # Wraps around
        self.assertEqual(new_time.minute, 30)

    def test_subtract_duration(self):
        """Test subtracting duration from time."""
        time = PlainTime(14, 30, 45)
        duration = Duration(hours=1, minutes=15)
        new_time = time.subtract(duration)
        self.assertEqual(new_time.hour, 13)
        self.assertEqual(new_time.minute, 15)

    def test_subtract_time(self):
        """Test subtracting time from time."""
        time1 = PlainTime(14, 30, 45)
        time2 = PlainTime(12, 15, 30)
        duration = time1.subtract(time2)
        self.assertEqual(duration.hours, 2)
        self.assertEqual(duration.minutes, 15)
        self.assertEqual(duration.seconds, 15)

    def test_with_fields(self):
        """Test with_fields method."""
        time = PlainTime(14, 30, 45)
        new_time = time.with_fields(hour=16, second=0)
        self.assertEqual(new_time.hour, 16)
        self.assertEqual(new_time.minute, 30)
        self.assertEqual(new_time.second, 0)

    def test_comparison(self):
        """Test time comparison."""
        time1 = PlainTime(14, 30, 45)
        time2 = PlainTime(16, 0, 0)
        time3 = PlainTime(14, 30, 45)

        self.assertLess(time1, time2)
        self.assertGreater(time2, time1)
        self.assertEqual(time1, time3)
        self.assertLessEqual(time1, time3)
        self.assertGreaterEqual(time1, time3)

    def test_string_representation(self):
        """Test string representation."""
        time = PlainTime(14, 30, 45)
        self.assertEqual(str(time), "14:30:45")

        time_with_micro = PlainTime(14, 30, 45, 123456)
        self.assertEqual(str(time_with_micro), "14:30:45.123456")

    def test_from_string(self):
        """Test creating time from string."""
        time = PlainTime.from_string("14:30:45")
        self.assertEqual(time.hour, 14)
        self.assertEqual(time.minute, 30)
        self.assertEqual(time.second, 45)

        time_with_micro = PlainTime.from_string("14:30:45.123456")
        self.assertEqual(time_with_micro.microsecond, 123456)


if __name__ == "__main__":
    unittest.main()
