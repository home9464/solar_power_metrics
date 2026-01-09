import minimalmodbus
import time

# Scan Inverter 1
try:
    instrument = minimalmodbus.Instrument('/dev/ttyACM0', 1)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.5
    
    print("--- Scanning Inverter 1 (Holding Registers 500-600) ---")
    for reg in range(500, 600):
        try:
            val = instrument.read_register(reg, 0, functioncode=3) # FC3 is default but being explicit
            # Filter out 0s to reduce noise, unless useful
            if val > 0:
                print(f"Reg {reg}: {val}")
        except Exception as e:
            # print(f"Reg {reg}: Error {e}")
            pass
        time.sleep(0.02)
except Exception as e:
    print(f"Main Error: {e}")
