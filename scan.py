import minimalmodbus
import serial

# --- ECO-WORTHY 5KW CONFIG ---
PORT = '/dev/ttyACM0'
SLAVE_ID = 1

# Addresses based on SRNE/Eco-Worthy Protocol
REG_BATTERY_SOC = 256  # 0x0100
REG_PV_TODAY = 275     # 0x0113
# -----------------------------

def read_eco_worthy():
    # Initialize instrument
    instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 1.0
    instrument.mode = minimalmodbus.MODE_RTU

    print(f"--- Querying Eco-Worthy 5kW on {PORT} ---")

    try:
        # Read SOC (Function code 3 is standard for SRNE/Eco-Worthy)
        # Scaling is usually 1:1 for SOC
        soc = instrument.read_register(REG_BATTERY_SOC, functioncode=3)
        
        # Read Solar Today 
        # Register 0x0113 usually returns Wh or 0.1kWh. 
        # If it returns Wh, we divide by 1000.
        pv_raw = instrument.read_register(REG_PV_TODAY, functioncode=3)
        pv_kwh = pv_raw / 10.0 # Adjust to /1000.0 if value seems too high

        print(f"✅ Connection Successful")
        print(f"Battery Remained: {soc}%")
        print(f"Solar Generated Today: {pv_kwh:.2f} kWh")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting Tip:")
        print("If you still see 'Illegal Address', try changing REG_BATTERY_SOC to 57345 (0xE001).")

if __name__ == "__main__":
    read_eco_worthy()