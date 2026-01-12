import minimalmodbus
import time

# --- CONFIG ---
PORT = '/dev/ttyACM0'
SLAVE_ID = 1

def scan_registers():
    instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.5
    instrument.mode = minimalmodbus.MODE_RTU

    # List of candidate registers for PV Power (W)
    pv_power_regs = [261, 263, 265, 266, 531]
    
    # List of candidate registers for PV Today (kWh or 0.1 kWh)
    pv_today_regs = [267, 275, 549, 61487]

    print("--- PV POWER CANDIDATES (Watts) ---")
    for reg in pv_power_regs:
        try:
            val = instrument.read_register(reg, functioncode=3)
            print(f"Register {reg:5} (0x{reg:04X}): {val} W")
        except Exception as e:
            print(f"Register {reg:5} (0x{reg:04X}): Error ({e})")
        time.sleep(0.1)

    print("\n--- PV TODAY CANDIDATES (kWh / 0.1 kWh) ---")
    for reg in pv_today_regs:
        try:
            val = instrument.read_register(reg, functioncode=3)
            print(f"Register {reg:5} (0x{reg:04X}): {val} (raw)")
            print(f"             Scaled (x0.1): {val * 0.1:.1f} kWh")
        except Exception as e:
            print(f"Register {reg:5} (0x{reg:04X}): Error ({e})")
        time.sleep(0.1)

if __name__ == "__main__":
    scan_registers()
