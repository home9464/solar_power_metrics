import minimalmodbus
import serial

# --- ADJUST THESE FOR YOUR INVERTER ---
PORT = '/dev/ttyACM0'
SLAVE_ID = 1

# EXAMPLE: Settings for Sunsynk/Deye (Change these based on the table above)
REG_BATTERY_SOC = 184  
REG_PV_TODAY = 108
FUNC_CODE = 3 # Try 3 or 4
# --------------------------------------

def read_solar():
    instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 1
    instrument.mode = minimalmodbus.MODE_RTU

    try:
        # Read Battery SOC
        # Some inverters require function code 4 (read_input_register)
        soc = instrument.read_register(REG_BATTERY_SOC, functioncode=FUNC_CODE)
        
        # Read PV Today (Assuming 0.1kWh scaling)
        pv_today = instrument.read_register(REG_PV_TODAY, decimals=1, functioncode=FUNC_CODE)

        print(f"✅ Success!")
        print(f"Battery Capacity: {soc}%")
        print(f"Solar Generated Today: {pv_today} kWh")

    except minimalmodbus.IllegalRequestError:
        print("❌ Error: Illegal Data Address.")
        print(f"The inverter does not have a register at {REG_BATTERY_SOC}.")
        print("Action: Check your manual for the 'Modbus RTU Register Map'.")
    except Exception as e:
        print(f"❌ Communication Error: {e}")

if __name__ == "__main__":
    read_solar()