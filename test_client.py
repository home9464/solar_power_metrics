import unittest
import sys
from unittest.mock import MagicMock

# Mock hardware libraries before importing client
sys.modules["luma"] = MagicMock()
sys.modules["luma.led_matrix"] = MagicMock()
sys.modules["luma.led_matrix.device"] = MagicMock()
sys.modules["luma.core"] = MagicMock()
sys.modules["luma.core.interface"] = MagicMock()
sys.modules["luma.core.interface.serial"] = MagicMock()
sys.modules["luma.core.virtual"] = MagicMock()

# Now we can import the client
import client

class TestSolarClient(unittest.TestCase):
    
    def test_format_power(self):
        # format_power(batt, pv, load)
        # _fmt: >=10 -> "12", <10 -> "9.8"
        
        # Case 1: Small numbers
        # batt=50, pv=5.59, load=2.12
        # Expect: "50 5.6 2.1"
        res = client.format_power(50, 5.59, 2.12)
        self.assertEqual(res, "50 5.6 2.1")
        
        # Case 2: Large numbers
        # batt=100, pv=12.5, load=10.1
        # Expect: "100 12 10"  (Note: batt is :02d, so 100 becomes 100? No, :02d for 100 is "100")
        # Wait, f"{100:02d}" is "100".
        res = client.format_power(100, 12.5, 10.1)
        self.assertEqual(res, "100 12 10")
        
        # Case 3: Mixed
        res = client.format_power(9, 0.5, 15.0)
        self.assertEqual(res, "09 0.5 15")

    def test_format_remaining_time_logic(self):
        # Battery capacity: 37.5 kWh
        # Min SOC: 10%
        # Usable = 37.5 * (SOC - 10)/100
        
        # Case 1: 50% SOC, 1.0 kW load
        # Usable = 37.5 * 0.4 = 15.0 kWh
        # Time = 15.0 / 1.0 = 15 hours
        # Format: "15.00"
        # Batt: "50"
        # String: "50" + spaces + "15.00"
        # "15.00" len is 5.
        # Wanted total digits 8. 
        # Batt (2) + TimeDigits (4 in 1500) = 6. 
        # Wait, the padding logic was: 
        # time_digits = len(time_str.replace('.', '')) -> len("1500") = 4
        # num_spaces = max(1, 6 - 4) = 2
        # Result: "50" + "  " + "15.00" = "50  15.00"
        res = client.format_remaining_time(50, 0, 1.0, 37.5, 10)
        self.assertEqual(res, "50  15.00")
        
        # Case 2: 20% SOC, 2.0 kW load
        # Usable = 37.5 * 0.1 = 3.75 kWh
        # Time = 3.75 / 2.0 = 1.875 hours
        # 0.875 * 60 = 52.5 -> 52 mins
        # Time str: "1.52"
        # time_digits = len("152") = 3
        # spaces = 6 - 3 = 3
        # Result: "20" + "   " + "1.52" = "20   1.52"
        res = client.format_remaining_time(20, 0, 2.0, 37.5, 10)
        self.assertEqual(res, "20   1.52")

    def test_format_remaining_time_large(self):
        # Case 3: Large time (Low load)
        # 90% SOC, 0.1 kW load
        # Usable = 37.5 * 0.8 = 30 kWh
        # Time = 30 / 0.1 = 300 hours
        # Time str: "300.00"
        # digits = 5 ("30000")
        # spaces = 6 - 5 = 1
        # Result: "90 300.00"
        res = client.format_remaining_time(90, 0, 0.1, 37.5, 10)
        self.assertEqual(res, "90 300.00")

    def test_format_remaining_time_overflow(self):
        # Case 4: Very low load (Infinite)
        # SOC 11%, Load 0.0001
        # Should cap at 999.59
        res = client.format_remaining_time(11, 0, 0.0, 37.5, 10)
        # 999.59
        # digits = 5 ("99959")
        # spaces = 1
        self.assertEqual(res, "11 999.59")

if __name__ == '__main__':
    unittest.main()
