import minimalmodbus
instrument = minimalmodbus.Instrument('/dev/ttyACM0', 2)
instrument.serial.baudrate = 9600

print("--- Scanning Inverter 2 (Input Registers ONLY) ---")
for reg in range(0, 700):
    try:
        # Specifically asking for Function Code 4
        val = instrument.read_register(reg, 0, functioncode=4)
        if 150 <= val <= 250:
            print(f"FC04 MATCH: Reg {reg} = {val}")
    except:
        continue