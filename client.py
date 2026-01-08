import re
import requests
import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import sevensegment

# --- CONFIGURATION ---
# The IP and port where your FastAPI server is running
SERVER_URL = "http://192.168.68.99:8000/metrics" 
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
    """Fetches the SystemSummary data from the server."""
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


def format_for_display(val:float):
    # This regex finds up to 4 digits and includes the dot if it exists
    # It stops exactly at 4 digits, regardless of where the dot is.
    match = re.search(r'^\d?\.?\d?\.?\d?\.?\d?', str(val).replace(' ', ''))
    truncated = match.group(0)
    
    # Calculate digit count (ignoring the dot) to determine padding
    digit_count = len(truncated.replace('.', ''))
    
    # Add leading spaces based on digit count (targeting width of 4)
    padding = " " * (4 - digit_count)
    return padding + truncated

# --- MAIN LOOP ---
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
            # Get float values from the summary
            solar_watts = summary.get('total_solar_kw', 0.0)
            load_watts = summary.get('total_load_kw', 0.0)
            avg_soc = summary.get('avg_battery_capacity_percentage', 0.0)
            total_daily_kwh = summary.get('total_daily_generation_kwh', 0.0)

            # Format each value using the new dynamic formatter
            pv_str = format_for_display(solar_watts)
            load_str = format_for_display(load_watts)
            battery_str = format_for_display(avg_soc)
            daily_str = format_for_display(total_daily_kwh)

            display_text = f"{pv_str}{load_str}{battery_str}{daily_str}"
            seg.text = display_text
            print(f"Displaying: [{display_text}]")
            time.sleep(2) # Refresh every 2 seconds
            
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
