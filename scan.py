import minimalmodbus
import serial

# --- ECO-WORTHY FINAL CONFIG ---
PORT = '/dev/ttyACM0'
SLAVE_ID = 1

def read_eco_worthy_metrics():
    # Setup instrument
    instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.5
    instrument.mode = minimalmodbus.MODE_RTU

    try:
        # 1. Battery Percentage (Register 256)
        # Function code 3, 0 decimals
        battery_soc = instrument.read_register(256, number_of_decimals=0, functioncode=3)
        
        # 2. Solar Energy Today (Register 275)
        # Using 1 decimal to convert (e.g.) 150 to 15.0 kWh
        # Note: If the result looks too small (like 0.1), 
        # change number_of_decimals to 0 and divide by 1000 manually.
        solar_today = instrument.read_register(275, number_of_decimals=1, functioncode=3)
        
        # 3. Solar Input Power (Register 263)
        solar_watts = instrument.read_register(263, number_of_decimals=0, functioncode=3)

        print("=" * 35)
        print(f"       ECO-WORTHY 5KW DATA       ")
        print("=" * 35)
        print(f"🔋 Battery Level:    {battery_soc}%")
        print(f"☀️ Solar Today:     {solar_today} kWh")
        print(f"⚡ Current PV Power: {solar_watts} W")
        print("=" * 35)

    except Exception as e:
        print(f"❌ Error reading metrics: {e}")

if __name__ == "__main__":
    read_eco_worthy_metrics()