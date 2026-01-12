import minimalmodbus
import serial
import time

# --- CONFIG ---
PORT = '/dev/ttyACM0'
SLAVE_ID = 1
BAUD = 9600 # Try 115200 if 9600 continues to fail

def scan_registers(start, end):
    instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
    instrument.serial.baudrate = BAUD
    instrument.serial.timeout = 0.2  # Short timeout for scanning
    instrument.mode = minimalmodbus.MODE_RTU
    
    print(f"--- Scanning {PORT} (Baud: {BAUD}, ID: {SLAVE_ID}) ---")
    print(f"Range: {start} to {end}\n")

    found_any = False
    for addr in range(start, end + 1):
        for fc in [3, 4]: # Try both Holding and Input registers
            try:
                # We use read_register directly to check for a response
                val = instrument.read_register(addr, functioncode=fc)
                print(f"✅ [ADDR {addr}] FC{fc} returned: {val}")
                found_any = True
            except Exception:
                # Silent skip for failed addresses
                continue
        
        # Small sleep to prevent flooding the inverter's serial buffer
        time.sleep(0.01)

    if not found_any:
        print("❌ No registers responded in this range.")
        print("Tip: If you get zero hits, swap your A and B wires and run again.")

if __name__ == "__main__":
    scan_registers(250, 300)