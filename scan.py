import minimalmodbus
import serial

# --- CONFIGURATION ---
PORT = '/dev/ttyACM0'
SLAVE_ADDRESS = 1  # Usually 1 by default for inverters
BAUDRATE = 9600    # Common: 9600, 19200, or 115200
# ---------------------

def read_inverter():
    try:
        # Initialize instrument
        instrument = minimalmodbus.Instrument(PORT, SLAVE_ADDRESS)
        
        # Serial Port Settings
        instrument.serial.baudrate = BAUDRATE
        instrument.serial.bytesize = 8
        instrument.serial.parity   = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout  = 0.5  # Seconds
        instrument.mode = minimalmodbus.MODE_RTU
        
        # Optional: Print debug info if having trouble
        # instrument.debug = True

        print(f"--- Connecting to Inverter on {PORT} ---")

        # 1. Read Battery Capacity (%)
        # Register 100 is a common placeholder; '0' decimals means it returns integer 0-100
        battery_soc = instrument.read_register(100, functioncode=3)
        
        # 2. Read Total Energy Generated Today (kWh)
        # Often stored as 'Value * 0.1'. 1 decimal divides the result by 10 automatically.
        pv_energy_today = instrument.read_register(110, number_of_decimals=1, functioncode=3)

        # Output Results
        print(f"Battery Remained: {battery_soc}%")
        print(f"Solar Energy Today: {pv_energy_today} kWh")

    except Exception as e:
        print(f"Error reading from inverter: {e}")

if __name__ == "__main__":
    read_inverter()