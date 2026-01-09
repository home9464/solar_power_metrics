import minimalmodbus
import time
import sys

PORT = '/dev/ttyACM0'

def scan_inverter(instrument, address):
    print(f"\n--- Scanning Inverter {address} (Holding Registers 500-600) ---")
    try:
        instrument.address = address
        found_any = False
        for reg in range(500, 600):
            try:
                val = instrument.read_register(reg, 0, functioncode=3)
                if val > 0:
                    print(f"Reg {reg}: {val}")
                    found_any = True
            except Exception as e:
                print(f"Reg {reg} error: {e}")
                pass
            time.sleep(0.02)
            
        if not found_any:
            print(f"No non-zero values found for Inverter {address} in range 500-600.")
            
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
