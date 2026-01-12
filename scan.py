import minimalmodbus

# --- ECO-WORTHY FINAL CONFIG ---
PORT = '/dev/ttyACM0'
SLAVE_ID = 1

def read_eco_worthy_metrics():
    instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.5
    instrument.mode = minimalmodbus.MODE_RTU

    try:
        # 1. Battery Percentage (Register 256)
        battery_soc = instrument.read_register(256, functioncode=3)
        
        # 2. Solar Energy Today (Register 275)
        # Scaling for SRNE is usually 0.1 kWh
        solar_today = instrument.read_register(275, decimals=1, functioncode=3)
        
        # 3. Solar Input Power (Register 263 - common on some models)
        solar_watts = instrument.read_register(263, functioncode=3)

        print("-" * 30)
        print(f"🔋 Battery Level:    {battery_soc}%")
        print(f"☀️ Solar Today:     {solar_today} kWh")
        print(f"⚡ Current PV Power: {solar_watts} W")
        print("-" * 30)

    except Exception as e:
        print(f"Error reading metrics: {e}")

if __name__ == "__main__":
    read_eco_worthy_metrics()