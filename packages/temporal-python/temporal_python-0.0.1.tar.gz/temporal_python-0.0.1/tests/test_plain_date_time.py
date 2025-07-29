"""
Tests for PlainDateTime class.
"""

import unittest
from temporal import PlainDateTime, PlainDate, PlainTime, Duration, Calendar
from temporal.exceptions import InvalidArgumentError, RangeError


class TestPlainDateTime(unittest.TestCase):
    
    def test_constructor(self):
        """Test PlainDateTime constructor."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45, 123456)
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.day, 15)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)
        self.assertEqual(dt.second, 45)
        self.assertEqual(dt.microsecond, 123456)
    
    def test_constructor_with_calendar(self):
        """Test PlainDateTime constructor with calendar."""
        calendar = Calendar("iso8601")
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45, calendar=calendar)
        self.assertEqual(dt.calendar, calendar)
    
    def test_to_plain_date(self):
        """Test conversion to PlainDate."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
        date = dt.to_plain_date()
        self.assertIsInstance(date, PlainDate)
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 15)
    
    def test_to_plain_time(self):
        """Test conversion to PlainTime."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45, 123456)
        time = dt.to_plain_time()
        self.assertIsInstance(time, PlainTime)
        self.assertEqual(time.hour, 14)
        self.assertEqual(time.minute, 30)
        self.assertEqual(time.second, 45)
        self.assertEqual(time.microsecond, 123456)
    
    def test_add_duration(self):
        """Test adding duration to datetime."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
        duration = Duration(days=1, hours=2)
        new_dt = dt.add(duration)
        self.assertEqual(new_dt.day, 16)
        self.assertEqual(new_dt.hour, 16)
    
    def test_subtract_duration(self):
        """Test subtracting duration from datetime."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
        duration = Duration(days=1, hours=2)
        new_dt = dt.subtract(duration)
        self.assertEqual(new_dt.day, 14)
        self.assertEqual(new_dt.hour, 12)
    
    def test_subtract_datetime(self):
        """Test subtracting datetime from datetime."""
        dt1 = PlainDateTime(2023, 6, 16, 14, 30, 45)
        dt2 = PlainDateTime(2023, 6, 15, 12, 15, 30)
        duration = dt1.subtract(dt2)
        self.assertEqual(duration.days, 1)
        self.assertEqual(duration.hours, 2)
        self.assertEqual(duration.minutes, 15)
        self.assertEqual(duration.seconds, 15)
    
    def test_with_fields(self):
        """Test with_fields method."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
        new_dt = dt.with_fields(year=2024, hour=16)
        self.assertEqual(new_dt.year, 2024)
        self.assertEqual(new_dt.hour, 16)
        self.assertEqual(new_dt.month, 6)  # Unchanged
    
    def test_comparison(self):
        """Test datetime comparison."""
        dt1 = PlainDateTime(2023, 6, 15, 14, 30, 45)
        dt2 = PlainDateTime(2023, 6, 15, 16, 0, 0)
        dt3 = PlainDateTime(2023, 6, 15, 14, 30, 45)
        
        self.assertLess(dt1, dt2)
        self.assertGreater(dt2, dt1)
        self.assertEqual(dt1, dt3)
    
    def test_string_representation(self):
        """Test string representation."""
        dt = PlainDateTime(2023, 6, 15, 14, 30, 45)
        self.assertEqual(str(dt), "2023-06-15T14:30:45")
        
        dt_with_micro = PlainDateTime(2023, 6, 15, 14, 30, 45, 123456)
        self.assertEqual(str(dt_with_micro), "2023-06-15T14:30:45.123456")
    
    def test_from_string(self):
        """Test creating datetime from string."""
        dt = PlainDateTime.from_string("2023-06-15T14:30:45")
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.day, 15)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)
        self.assertEqual(dt.second, 45)
    
    def test_now(self):
        """Test now method."""
        now = PlainDateTime.now()
        self.assertIsInstance(now, PlainDateTime)
        self.assertGreaterEqual(now.year, 2023)


if __name__ == "__main__":
    unittest.main()
