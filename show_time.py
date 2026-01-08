import time
from datetime import datetime
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import sevensegment

def main():
    try:
        serial = spi(port=0, device=0, gpio=noop())
        device = max7219(serial, cascaded=1)  # 1 display. 
        seg = sevensegment(device)
        # Set brightness (0-255)
        device.contrast(10) 
        print("LED Matrix initialized.")
        print("Displaying time (Ctrl+C to stop)...")
        
        while True:
            now = datetime.now()
            # Format: HH.MM.SS
            time_str = now.strftime("%H.%M.%S")
            seg.text = time_str
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting...")
        pass
    except Exception as e:
        print(f"Hardware Error: Could not initialize LED matrix: {e}")
        print("This script requires 'luma.led_matrix' and SPI enabled.")

if __name__ == '__main__':
    main()
