"""
Tests for ZonedDateTime class.
"""

import unittest

from temporal import Calendar, Duration, TimeZone, ZonedDateTime
from temporal.exceptions import InvalidArgumentError


class TestZonedDateTime(unittest.TestCase):
    def test_constructor(self):
        """Test ZonedDateTime constructor."""
        tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, 123456, tz)
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.day, 15)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)
        self.assertEqual(dt.second, 45)
        self.assertEqual(dt.microsecond, 123456)
        self.assertEqual(dt.timezone, tz)

    def test_constructor_requires_timezone(self):
        """Test that constructor requires timezone."""
        with self.assertRaises(InvalidArgumentError):
            ZonedDateTime(2023, 6, 15, 14, 30, 45)

    def test_offset_string(self):
        """Test offset string representation."""
        utc_tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=utc_tz)
        self.assertEqual(dt.offset_string, "Z")

    def test_to_instant(self):
        """Test conversion to Instant."""
        tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
        instant = dt.to_instant()
        self.assertGreater(instant.epoch_seconds, 0)

    def test_to_plain_date_time(self):
        """Test conversion to PlainDateTime."""
        tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
        plain_dt = dt.to_plain_date_time()
        self.assertEqual(plain_dt.year, 2023)
        self.assertEqual(plain_dt.hour, 14)

    def test_with_timezone(self):
        """Test timezone conversion."""
        utc_tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=utc_tz)

        # Convert to different timezone (if available)
        try:
            est_tz = TimeZone("US/Eastern")
            est_dt = dt.with_timezone(est_tz)
            self.assertEqual(est_dt.timezone, est_tz)
            # Time should be different but instant should be same
            self.assertEqual(dt.to_instant(), est_dt.to_instant())
        except InvalidArgumentError:
            # Skip if timezone not available
            pass

    def test_add_duration(self):
        """Test adding duration to zoned datetime."""
        tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
        duration = Duration(hours=2, minutes=30)
        new_dt = dt.add(duration)
        self.assertEqual(new_dt.hour, 17)
        self.assertEqual(new_dt.minute, 0)

    def test_subtract_duration(self):
        """Test subtracting duration from zoned datetime."""
        tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
        duration = Duration(hours=1)
        new_dt = dt.subtract(duration)
        self.assertEqual(new_dt.hour, 13)

    def test_subtract_zoned_datetime(self):
        """Test subtracting zoned datetime from zoned datetime."""
        tz = TimeZone("UTC")
        dt1 = ZonedDateTime(2023, 6, 15, 16, 0, 0, timezone=tz)
        dt2 = ZonedDateTime(2023, 6, 15, 14, 30, 0, timezone=tz)
        duration = dt1.subtract(dt2)
        self.assertEqual(duration.hours, 1)
        self.assertEqual(duration.minutes, 30)

    def test_comparison(self):
        """Test zoned datetime comparison."""
        tz = TimeZone("UTC")
        dt1 = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
        dt2 = ZonedDateTime(2023, 6, 15, 16, 0, 0, timezone=tz)
        dt3 = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)

        self.assertLess(dt1, dt2)
        self.assertGreater(dt2, dt1)
        self.assertEqual(dt1, dt3)

    def test_string_representation(self):
        """Test string representation."""
        tz = TimeZone("UTC")
        dt = ZonedDateTime(2023, 6, 15, 14, 30, 45, timezone=tz)
        self.assertIn("2023-06-15T14:30:45", str(dt))
        # Check string contains Z or +00:00
        dt_str = str(dt)
        self.assertTrue("Z" in dt_str or "+00:00" in dt_str)

    def test_now(self):
        """Test now method."""
        tz = TimeZone("UTC")
        now = ZonedDateTime.now(tz)
        self.assertIsInstance(now, ZonedDateTime)
        self.assertEqual(now.timezone, tz)


if __name__ == "__main__":
    unittest.main()
