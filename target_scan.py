import minimalmodbus
import time

# Targets for Inverter 1
# Yield: 17.6 kWh -> Look for 176 (x0.1), 1760 (x0.01), 17600 (x0.001)
# PV Voltage: 396 V -> Look for 396, 3960
# Temp: 32 C -> Look for 32, 320

TARGETS = {
    "Yield_17.6": [17, 18, 175, 176, 177, 1760, 17600],
    "PV_V_396": [395, 396, 397, 3960],
    "Temp_32": [31, 32, 33, 320]
}

def scan_inverter(instrument, address):
    print(f"\n--- Scanning Inverter {address} (0-1000) for Targets ---")
    instrument.address = address
    for reg in range(0, 1000):
        try:
            val = instrument.read_register(reg, 0, functioncode=3)
            
            # Check matches
            if val in TARGETS["Yield_17.6"]:
                print(f"[Inv {address}] Reg {reg} = {val} (Possible YIELD)")
            if val in TARGETS["PV_V_396"]:
                print(f"[Inv {address}] Reg {reg} = {val} (Possible PV VOLT)")
            if val in TARGETS["Temp_32"]:
                print(f"[Inv {address}] Reg {reg} = {val} (Possible TEMP)")
                
        except Exception:
            pass
        
        if reg % 100 == 0:
            time.sleep(0.02)

try:
    instrument = minimalmodbus.Instrument('/dev/ttyACM0', 1)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.2
    
    scan_inverter(instrument, 1)
    scan_inverter(instrument, 2)

except Exception as e:
    print(e)
