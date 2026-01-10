import minimalmodbus
import time
import sys

PORT = '/dev/ttyACM0'

def scan_inverter(instrument, address):
    print(f"\n--- Scanning Inverter {address} (Holding Registers 0-1200) ---")
    try:
        instrument.address = address
        found_any = False
        # Extended range to find PV Today (17.6 -> 176, 1760, 17600)
        for reg in range(0, 1200):
            try:
                val = instrument.read_register(reg, 0, functioncode=3)
                if val > 0:
                    suffix = ""
                    # 17.6 kWh
                    if 170 <= val <= 180: suffix += " [Possible YIELD 17.6]"
                    if 1750 <= val <= 1770: suffix += " [Possible YIELD 17.6]"
                    # 396 V
                    if 390 <= val <= 400: suffix += " [Possible PV VOLT 396]"
                    # 32 C
                    if 30 <= val <= 34: suffix += " [Possible TEMP 32]"
                    
                    # Only print if it matches a target or stands out
                    if suffix or (200 <= reg <= 600): # Keep seeing old range too
                        print(f"Reg {reg}: {val}{suffix}")
                        found_any = True
            except Exception:
                pass
            
            if reg % 50 == 0:
                time.sleep(0.01)
            
        if not found_any:
            print(f"No non-zero values found for Inverter {address}.")
            
    except Exception as e:
        print(f"Failed to scan Inverter {address}: {e}")

try:
    instrument = minimalmodbus.Instrument(PORT, 1)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.5
    # instrument.clear_buffers_before_each_transaction = True
    
    # Scan Inverter 1
    scan_inverter(instrument, 1)
    
    # Scan Inverter 2
    scan_inverter(instrument, 2)

except Exception as e:
    print(f"Could not open serial port {PORT}: {e}")
    sys.exit(1)
