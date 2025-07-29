"""
Tests for Duration class.
"""

import unittest
from temporal import Duration
from temporal.exceptions import InvalidArgumentError


class TestDuration(unittest.TestCase):
    
    def test_constructor(self):
        """Test Duration constructor."""
        duration = Duration(years=1, months=2, days=3, hours=4, minutes=5, seconds=6, microseconds=7)
        self.assertEqual(duration.years, 1)
        self.assertEqual(duration.months, 2)
        self.assertEqual(duration.days, 3)
        self.assertEqual(duration.hours, 4)
        self.assertEqual(duration.minutes, 5)
        self.assertEqual(duration.seconds, 6)
        self.assertEqual(duration.microseconds, 7)
    
    def test_constructor_defaults(self):
        """Test Duration constructor with defaults."""
        duration = Duration()
        self.assertEqual(duration.years, 0)
        self.assertEqual(duration.months, 0)
        self.assertEqual(duration.days, 0)
        self.assertEqual(duration.hours, 0)
        self.assertEqual(duration.minutes, 0)
        self.assertEqual(duration.seconds, 0)
        self.assertEqual(duration.microseconds, 0)
    
    def test_normalization(self):
        """Test duration normalization."""
        duration = Duration(seconds=3661)  # 1 hour, 1 minute, 1 second
        self.assertEqual(duration.hours, 1)
        self.assertEqual(duration.minutes, 1)
        self.assertEqual(duration.seconds, 1)
    
    def test_total_seconds(self):
        """Test total_seconds calculation."""
        duration = Duration(days=1, hours=1, minutes=1, seconds=1)
        expected = 24 * 3600 + 3600 + 60 + 1
        self.assertEqual(duration.total_seconds(), expected)
    
    def test_add(self):
        """Test adding durations."""
        duration1 = Duration(hours=1, minutes=30)
        duration2 = Duration(hours=2, minutes=45)
        result = duration1.add(duration2)
        self.assertEqual(result.hours, 4)
        self.assertEqual(result.minutes, 15)
    
    def test_subtract(self):
        """Test subtracting durations."""
        duration1 = Duration(hours=3, minutes=45)
        duration2 = Duration(hours=1, minutes=30)
        result = duration1.subtract(duration2)
        self.assertEqual(result.hours, 2)
        self.assertEqual(result.minutes, 15)
    
    def test_negated(self):
        """Test negating duration."""
        duration = Duration(hours=1, minutes=30)
        negated = duration.negated()
        self.assertEqual(negated.hours, -1)
        self.assertEqual(negated.minutes, -30)
    
    def test_abs(self):
        """Test absolute value of duration."""
        duration = Duration(hours=-1, minutes=-30)
        abs_duration = duration.abs()
        self.assertEqual(abs_duration.hours, 1)
        self.assertEqual(abs_duration.minutes, 30)
    
    def test_with_fields(self):
        """Test with_fields method."""
        duration = Duration(hours=1, minutes=30)
        new_duration = duration.with_fields(hours=2, seconds=45)
        self.assertEqual(new_duration.hours, 2)
        self.assertEqual(new_duration.minutes, 30)
        self.assertEqual(new_duration.seconds, 45)
    
    def test_string_representation(self):
        """Test string representation."""
        duration = Duration(days=1, hours=2, minutes=30, seconds=45)
        duration_str = str(duration)
        self.assertIn("P1D", duration_str)
        self.assertIn("T2H30M45S", duration_str)
    
    def test_zero_duration_string(self):
        """Test zero duration string representation."""
        duration = Duration()
        self.assertEqual(str(duration), "PT0S")
    
    def test_from_string(self):
        """Test creating duration from string."""
        duration = Duration.from_string("P1DT2H30M45S")
        self.assertEqual(duration.days, 1)
        self.assertEqual(duration.hours, 2)
        self.assertEqual(duration.minutes, 30)
        self.assertEqual(duration.seconds, 45)
    
    def test_from_string_fractional_seconds(self):
        """Test creating duration from string with fractional seconds."""
        duration = Duration.from_string("PT1.5S")
        self.assertEqual(duration.seconds, 1)
        self.assertEqual(duration.microseconds, 500000)
    
    def test_equality(self):
        """Test duration equality."""
        duration1 = Duration(hours=1, minutes=30)
        duration2 = Duration(hours=1, minutes=30)
        duration3 = Duration(hours=2, minutes=0)
        
        self.assertEqual(duration1, duration2)
        self.assertNotEqual(duration1, duration3)
    
    def test_operators(self):
        """Test duration operators."""
        duration1 = Duration(hours=1)
        duration2 = Duration(minutes=30)
        
        added = duration1 + duration2
        self.assertEqual(added.hours, 1)
        self.assertEqual(added.minutes, 30)
        
        subtracted = duration1 - duration2
        self.assertEqual(subtracted.hours, 1)
        self.assertEqual(subtracted.minutes, -30)
        
        negated = -duration1
        self.assertEqual(negated.hours, -1)
        
        abs_negated = abs(negated)
        self.assertEqual(abs_negated.hours, 1)


if __name__ == "__main__":
    unittest.main()
