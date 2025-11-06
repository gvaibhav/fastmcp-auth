"""
Comprehensive test suite for Time MCP Server
Updated to match official MCP time server tool signatures
Test-Driven Development approach using unittest
"""

import unittest
import asyncio
import sys
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Import the functions we're testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pylint: disable=import-error,wrong-import-position
from time_mcp_server import get_current_time, convert_time


class TestGetCurrentTime(unittest.TestCase):
    """Test suite for get_current_time tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_get_current_time_utc_default(self):
        """Test getting current time with default UTC timezone"""
        result = self.loop.run_until_complete(get_current_time())
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn('timezone', result)
        self.assertIn('datetime', result)
        self.assertIn('is_dst', result)
        
        # Verify timezone is UTC
        self.assertEqual(result['timezone'], 'UTC')
        
        # Verify datetime is valid ISO 8601
        parsed = datetime.fromisoformat(result['datetime'])
        self.assertIsNotNone(parsed.tzinfo)
        
        # Verify it's approximately current time (within 5 seconds)
        now = datetime.now(timezone.utc)
        time_diff = abs((parsed - now).total_seconds())
        self.assertLess(time_diff, 5)
        
        # Verify is_dst is boolean
        self.assertIsInstance(result['is_dst'], bool)
    
    def test_get_current_time_specific_timezone(self):
        """Test getting current time in specific timezone"""
        result = self.loop.run_until_complete(
            get_current_time(timezone="America/New_York")
        )
        
        self.assertEqual(result['timezone'], 'America/New_York')
        parsed = datetime.fromisoformat(result['datetime'])
        # Some ISO parsers return a fixed-offset tzinfo while ZoneInfo preserves the zone key.
        # Compare offsets instead to be robust across environments.
        expected_offset = parsed.replace(tzinfo=ZoneInfo("America/New_York")).utcoffset()
        self.assertEqual(parsed.utcoffset(), expected_offset)
    
    def test_get_current_time_various_timezones(self):
        """Test multiple valid timezones"""
        timezones = [
            "UTC",
            "America/Los_Angeles",
            "Europe/London",
            "Asia/Tokyo",
            "Australia/Sydney",
        ]
        
        for tz in timezones:
            with self.subTest(timezone=tz):
                result = self.loop.run_until_complete(get_current_time(timezone=tz))
                self.assertEqual(result['timezone'], tz)
                parsed = datetime.fromisoformat(result['datetime'])
                self.assertIsNotNone(parsed.tzinfo)
    
    def test_get_current_time_invalid_timezone(self):
        """Test error handling for invalid timezone"""
        with self.assertRaises(ValueError) as context:
            self.loop.run_until_complete(get_current_time(timezone="Invalid/Timezone"))
        
        self.assertIn("Invalid timezone", str(context.exception))
    
    def test_get_current_time_empty_string_timezone(self):
        """Test error handling for empty timezone string"""
        with self.assertRaises(ValueError):
            self.loop.run_until_complete(get_current_time(timezone=""))
    
    def test_get_current_time_dst_field(self):
        """Test that DST field is properly set"""
        # Test during known DST period (summer)
        result = self.loop.run_until_complete(get_current_time(timezone="America/New_York"))
        self.assertIn('is_dst', result)
        self.assertIsInstance(result['is_dst'], bool)
    
    def test_get_current_time_response_format(self):
        """Test that response has all required fields"""
        result = self.loop.run_until_complete(get_current_time(timezone="UTC"))
        
        # Check all required fields are present
        required_fields = ['timezone', 'datetime', 'is_dst']
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")


class TestConvertTime(unittest.TestCase):
    """Test suite for convert_time tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_convert_time_basic(self):
        """Test basic time conversion with HH:MM format"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="14:30",
                target_timezone="America/New_York"
            )
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn('source', result)
        self.assertIn('target', result)
        self.assertIn('time_difference', result)
        
        # Verify source structure
        self.assertIn('timezone', result['source'])
        self.assertIn('datetime', result['source'])
        self.assertIn('is_dst', result['source'])
        
        # Verify target structure
        self.assertIn('timezone', result['target'])
        self.assertIn('datetime', result['target'])
        self.assertIn('is_dst', result['target'])
    
    def test_convert_time_offset_calculation(self):
        """Test that timezone offset is calculated correctly"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="14:00",
                target_timezone="America/New_York"
            )
        )
        
        _ = datetime.fromisoformat(result['source']['datetime'])  # source_dt unused
        target_dt = datetime.fromisoformat(result['target']['datetime'])
        
        # Verify the hour changed correctly
        # EST is UTC-5, so 14:00 UTC should be 09:00 EST
        self.assertEqual(target_dt.hour, 9)
    
    def test_convert_time_same_timezone(self):
        """Test converting within the same timezone"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="14:30",
                target_timezone="UTC"
            )
        )
        
        source_dt = datetime.fromisoformat(result['source']['datetime'])
        target_dt = datetime.fromisoformat(result['target']['datetime'])
        
        # Same timezone should have same time
        self.assertEqual(source_dt.hour, target_dt.hour)
        self.assertEqual(source_dt.minute, target_dt.minute)
        self.assertEqual(result['time_difference'], '+0.0h')
    
    def test_convert_time_across_date_line(self):
        """Test conversion that crosses date boundary"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="America/Los_Angeles",
                time="23:00",
                target_timezone="Asia/Tokyo"
            )
        )
        
        source_dt = datetime.fromisoformat(result['source']['datetime'])
        target_dt = datetime.fromisoformat(result['target']['datetime'])
        
        # Tokyo is ahead, so should be next day
        self.assertNotEqual(source_dt.day, target_dt.day)
    
    def test_convert_time_invalid_source_timezone(self):
        """Test error handling for invalid source timezone"""
        with self.assertRaises(ValueError) as context:
            self.loop.run_until_complete(
                convert_time(
                    source_timezone="Invalid/Source",
                    time="14:30",
                    target_timezone="UTC"
                )
            )
        
        self.assertIn("Invalid source timezone", str(context.exception))
    
    def test_convert_time_invalid_target_timezone(self):
        """Test error handling for invalid target timezone"""
        with self.assertRaises(ValueError) as context:
            self.loop.run_until_complete(
                convert_time(
                    source_timezone="UTC",
                    time="14:30",
                    target_timezone="Invalid/Target"
                )
            )
        
        self.assertIn("Invalid target timezone", str(context.exception))
    
    def test_convert_time_invalid_time_format(self):
        """Test error handling for invalid time format"""
        invalid_times = [
            "not-a-valid-time",
            "25:00",  # Invalid hour
            "14:60",  # Invalid minute
            "14",     # Missing minutes
            "14:30:00",  # Too many parts
            "",       # Empty string
        ]
        
        for invalid_time in invalid_times:
            with self.subTest(time=invalid_time):
                with self.assertRaises(ValueError) as context:
                    self.loop.run_until_complete(
                        convert_time(
                            source_timezone="UTC",
                            time=invalid_time,
                            target_timezone="America/New_York"
                        )
                    )
                
                self.assertIn("Invalid time format", str(context.exception))
    
    def test_convert_time_valid_formats(self):
        """Test various valid HH:MM formats"""
        valid_times = [
            "00:00",
            "09:30",
            "12:00",
            "23:59",
        ]
        
        for valid_time in valid_times:
            with self.subTest(time=valid_time):
                result = self.loop.run_until_complete(
                    convert_time(
                        source_timezone="UTC",
                        time=valid_time,
                        target_timezone="America/New_York"
                    )
                )
                self.assertIsNotNone(result)
    
    def test_convert_time_difference_format(self):
        """Test that time_difference is formatted correctly"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="12:00",
                target_timezone="Asia/Tokyo"
            )
        )
        
        time_diff = result['time_difference']
        
        # Should be in format like '+9.0h' or '-5.0h'
        self.assertRegex(time_diff, r'^[+-]\d+(\.\d+)?h$')
    
    def test_convert_time_midnight_boundary(self):
        """Test conversion at midnight"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="00:00",
                target_timezone="Asia/Tokyo"
            )
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['source']['timezone'], 'UTC')
        self.assertEqual(result['target']['timezone'], 'Asia/Tokyo')
    
    def test_convert_time_noon(self):
        """Test conversion at noon"""
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="12:00",
                target_timezone="America/New_York"
            )
        )
        
        source_dt = datetime.fromisoformat(result['source']['datetime'])
        self.assertEqual(source_dt.hour, 12)
        self.assertEqual(source_dt.minute, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_daylight_saving_time_aware(self):
        """Test that conversions handle DST correctly"""
        # Test with a timezone that observes DST
        result_ny = self.loop.run_until_complete(
            get_current_time(timezone="America/New_York")
        )
        
        # DST field should be present and boolean
        self.assertIn('is_dst', result_ny)
        self.assertIsInstance(result_ny['is_dst'], bool)
        
        # Test with a timezone that doesn't observe DST
        result_tokyo = self.loop.run_until_complete(
            get_current_time(timezone="Asia/Tokyo")
        )
        
        # Japan doesn't observe DST, so should be False
        self.assertFalse(result_tokyo['is_dst'])
    
    def test_fractional_timezone_offsets(self):
        """Test timezones with fractional hour offsets"""
        # Nepal is UTC+5:45
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time="12:00",
                target_timezone="Asia/Kathmandu"
            )
        )
        
        # Time difference should show fractional hours
        time_diff = result['time_difference']
        self.assertIn('.', time_diff)  # Should have decimal point
    
    def test_utc_timezone_variants(self):
        """Test different UTC timezone names"""
        utc_variants = ["UTC"]
        
        for tz in utc_variants:
            with self.subTest(timezone=tz):
                result = self.loop.run_until_complete(get_current_time(timezone=tz))
                self.assertIsNotNone(result)
    
    def test_extreme_time_differences(self):
        """Test conversion between timezones with large differences"""
        # Pacific/Kiritimati is UTC+14, American Samoa is UTC-11
        # That's a 25 hour difference (crossing date line)
        result = self.loop.run_until_complete(
            convert_time(
                source_timezone="Pacific/Samoa",
                time="12:00",
                target_timezone="Pacific/Kiritimati"
            )
        )
        
        source_dt = datetime.fromisoformat(result['source']['datetime'])
        target_dt = datetime.fromisoformat(result['target']['datetime'])
        
        # Should be different days
        self.assertNotEqual(source_dt.day, target_dt.day)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_get_and_convert_workflow(self):
        """Test realistic workflow: get current time and convert it"""
        # Get current time in UTC
        utc_result = self.loop.run_until_complete(get_current_time(timezone="UTC"))
        
        # Extract time in HH:MM format
        utc_dt = datetime.fromisoformat(utc_result['datetime'])
        time_str = utc_dt.strftime("%H:%M")
        
        # Convert to another timezone
        convert_result = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time=time_str,
                target_timezone="America/New_York"
            )
        )
        
        # Verify conversion makes sense
        self.assertIsNotNone(convert_result)
        self.assertIn('source', convert_result)
        self.assertIn('target', convert_result)
    
    def test_round_trip_conversion(self):
        """Test converting time and converting back"""
        original_time = "14:30"
        
        # UTC -> Tokyo
        to_tokyo = self.loop.run_until_complete(
            convert_time(
                source_timezone="UTC",
                time=original_time,
                target_timezone="Asia/Tokyo"
            )
        )
        
        # Extract Tokyo time
        tokyo_dt = datetime.fromisoformat(to_tokyo['target']['datetime'])
        tokyo_time = tokyo_dt.strftime("%H:%M")
        
        # Tokyo -> UTC (back)
        back_to_utc = self.loop.run_until_complete(
            convert_time(
                source_timezone="Asia/Tokyo",
                time=tokyo_time,
                target_timezone="UTC"
            )
        )
        
        # Should get back to original time
        utc_dt = datetime.fromisoformat(back_to_utc['target']['datetime'])
        final_time = utc_dt.strftime("%H:%M")
        
        self.assertEqual(original_time, final_time)


def run_tests():
    """Run all tests and generate coverage report"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGetCurrentTime))
    suite.addTests(loader.loadTestsFromTestCase(TestConvertTime))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print(f"{'='*70}\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
