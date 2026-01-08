import re
import requests
import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import sevensegment
from typing import Optional, Dict, Any, Union

# --- CONFIGURATION ---
# The IP and port where your FastAPI server is running
SERVER_URL = "http://192.168.68.99:8000/metrics" 
#SERVER_URL = "http://127.0.0.1:8000/test"
# Time in seconds to show each metric before cycling
CYCLE_TIME = 4 

# --- HARDWARE SETUP ---
try:
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=1)  # 1 display. 
    seg = sevensegment(device)
    # Set brightness (0-255)
    device.contrast(80) 
    print("LED Matrix initialized.")
except Exception as e:
    seg = None
    print(f"Hardware Error: Could not initialize LED matrix: {e}")
    print("This script requires 'luma.led_matrix' and SPI enabled.")
    #exit()

# --- FUNCTIONS ---
def get_system_summary() -> Union[Dict[str, Any], str, None]:
    """Fetches the SystemSummary data from the server.
    
    example data = {
        'total_load_kw': 2.1, 
        'total_pv_kw': 5.5, 
        'avg_battery_capacity_percentage': 20.9, 
        'total_pv_today_kwh': 23.6, 
        'details': []
    }

    """
    try:
        response = requests.get(SERVER_URL, timeout=2)
        response.raise_for_status() # Raises an exception for bad responses (4xx or 5xx) 
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching data: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def _fmt(val: float) -> str:
    if val >= 10:
        return f"{val:2.0f}" # "12"
    else:
        return f"{val:3.1f}" # "9.8" or "0.5"

def format_power(batt: int, pv: float, load: float) -> str:
    """
    Formats the power metrics string: "BB P.P L.L"
    Input: batt (int), pv_kw (float), load_kw (float)
    """
    # 1. Battery: 2 digits rounded/truncated
    batt_str = f"{batt:02d}"
    # 2. PV & Load: 2 digits wide
    pv_str = _fmt(pv)
    load_str = _fmt(load)
    # Combine with spaces
    # Resulting string example: "20 0.5 12"
    return f"{batt_str} {pv_str} {load_str}"

def format_remaining_time(batt: int, pv: float, load: float, battery_full_capacity_kwh: float, min_battery_percentage_usable: int) -> str:
    """
    Formats the remaining time string: "BB   H.MM"
    Input: batt (int), pv (float), load (float), battery_full_capacity_kwh (float), min_battery_percentage_usable (int)
    """
    batt_str = f"{batt:02d}"
    
    # Calculate usable energy
    # If SOC is below min, usable is 0. 
    soc_diff = max(0, batt - min_battery_percentage_usable)
    usable_energy_kwh = battery_full_capacity_kwh * (soc_diff / 100.0)

    # Calculate remaining time
    if load > 0.01: # Avoid division by zero
        remaining_hours = usable_energy_kwh / load
    else:
        remaining_hours = 999.99 # Effectively infinite
    
    # Cap max hours for display
    if remaining_hours > 999.99:
            remaining_hours = 999.99
    
    hours = int(remaining_hours)
    minutes = int((remaining_hours - hours) * 60)
    
    # Format: hhh.mm (e.g., "5.40", "500.15")
    # Cap at 999 hours to prevent total overflow of display if value is absurd
    if hours > 999:
        hours = 999
        minutes = 59
    
    time_str = f"{hours}.{minutes:02d}"
    
    # Calculate padding to satisfy 8 characters total length (excluding dots)
    # batt_str is 2 chars.
    # Total wanted = 8.
    # Remaining for spaces + time_digits = 6.
    time_digits = len(time_str.replace('.', ''))
    num_spaces = max(1, 6 - time_digits)
    
    return f"{batt_str}{' ' * num_spaces}{time_str}"

def main():
    """
    Main loop to fetch data and display combined metrics on the display.
    """
    print("Starting Solar Monitor client... Press Ctrl+C to exit.")
    # Text to show when data can't be fetched
    error_message = "SERVER OFFLINE   " # 16 chars
    while True:
        summary = get_system_summary()
        if summary is None:
            if seg is not None:
                seg.text = "0"
            print("[Error]")
            time.sleep(5)
        else:
            batt = int(summary['avg_battery_capacity_percentage'])
            pv = summary['total_pv_kw']
            load = summary['total_load_kw']
            batt_cap = summary['battery_full_capacity_kwh']
            min_soc = summary['min_battery_percentage_usable']

            power_string = format_power(batt, pv, load)
            remaining_time_string = format_remaining_time(batt, pv, load, batt_cap, min_soc)
            
            # Show power
            if seg is not None:
                seg.text = power_string
            print(f"{power_string}")
            time.sleep(CYCLE_TIME) 
            
            # Show remaining time
            if seg is not None:
                seg.text = remaining_time_string
            print(f"{remaining_time_string}")
            time.sleep(CYCLE_TIME)
        else:
            # If fetch fails, show an error and retry after a shorter delay
            if seg is not None:
                seg.text = error_message
            print(f"Error: [{error_message}]")
            time.sleep(5) # Shorter sleep to retry connection faster

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping client...")
        # Clear the display on exit
        try:
            seg.text = ""
        except NameError:
            pass # In case hardware init failed
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
