import re
import requests
import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import sevensegment

# --- CONFIGURATION ---
# The IP and port where your FastAPI server is running
SERVER_URL = "http://192.168.68.99:8000/metrics" 
#SERVER_URL = "http://192.168.68.99:8000/test" 
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
    print(f"Hardware Error: Could not initialize LED matrix: {e}")
    print("This script requires 'luma.led_matrix' and SPI enabled.")
    exit()

# --- FUNCTIONS ---
def get_system_summary():
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
        if e.response.status_code == 503:
            print("Server returned 503: No online inverters.")
            return "NO_INVERTERS"
        print(f"HTTP Error fetching data: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def format_power(val):
    if val >= 10:
        return f"{val:2.0f}" # "12"
    else:
        return f"{val:3.1f}" # "9.8" or "0.5"

def main():
    """
    Main loop to fetch data and display combined metrics on the display.
    """
    print("Starting Solar Monitor client... Press Ctrl+C to exit.")
    # Text to show when data can't be fetched
    error_message = "SERVER OFFLINE   " # 16 chars
    while True:
        summary = get_system_summary()
        if summary == "NO_INVERTERS":
            seg.text = "FAIL           "
            print("Displaying: [FAIL           ]")
            time.sleep(5)
        elif summary:
            batt = int(summary['avg_battery_capacity_percentage'])
            pv = summary['total_pv_kw']
            load = summary['total_load_kw']
            # 1. Battery: 2 digits rounded/truncated
            batt_str = f"{batt:02d}"
            # 2. PV & Load: 2 digits wide
            # We use :2g or custom logic to handle "12" vs "9.8" 
            pv_str = format_power(pv)
            load_str = format_power(load)
            # Combine with spaces
            # Resulting string example: "20 0.5 12"
            display_string = f"{batt_str} {pv_str} {load_str}"
            #display_text = f"{battery_reamining_percentage}"
            seg.text = display_string
            print(f"Data: {summary}, Displaying: {display_string}")
            time.sleep(10) # Refresh every 10 seconds
        else:
            # If fetch fails, show an error and retry after a shorter delay
            seg.text = error_message
            print(f"Displaying: [{error_message}]")
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
