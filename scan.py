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
        
        # 2. Solar Energy Today (Register 61487)
        # Scaling for SRNE is 0.1 kWh
        solar_today = instrument.read_register(61487, numberOfDecimals=1, functioncode=3)
        
        # 3. Solar Input Power (Register 265)
        solar_watts = instrument.read_register(265, functioncode=3)
        
        # 4. PV Voltage (Register 263)
        pv_volts = instrument.read_register(263, numberOfDecimals=1, functioncode=3)
        
        # 5. PV Current (Register 264)
        pv_amps = instrument.read_register(264, numberOfDecimals=1, functioncode=3)

        print("=" * 35)
        print(f"       ECO-WORTHY 5KW DATA       ")
        print("=" * 35)
        print(f"🔋 Battery Level:    {battery_soc}%")
        print(f"☀️ Solar Today:     {solar_today} kWh")
        print(f"⚡ Current PV Power: {solar_watts} W")
        print(f"🔌 PV Voltage:      {pv_volts} V")
        print(f"🔌 PV Current:      {pv_amps} A")
        print("=" * 35)

    except Exception as e:
        print(f"❌ Error reading metrics: {e}")

if __name__ == "__main__":
    read_eco_worthy_metrics()