import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import minimalmodbus
import serial
import asyncio
import random
from typing import List, Optional

DEBUG = True

# --- CONFIGURATION ---
PORT = '/dev/ttyACM0'  # Your USB adapter port
BAUDRATE = 9600        # Standard for SRNE/PowMr
INVERTER_IDS = [1, 2]  # The IDs set on your inverter LCD screens

# --- DATA MODELS ---
class SolarData(BaseModel):
    inverter_id: int
    status: str
    battery_capacity_percentage: Optional[float] = None
    solar_power_kw: Optional[float] = None
    load_power_kw: Optional[float] = None
    daily_generation_kwh: Optional[float] = None

class SystemSummary(BaseModel):
    total_solar_kw: float
    total_load_kw: float
    avg_battery_capacity_percentage: float
    total_daily_generation_kwh: float
    details: List[SolarData]

# --- HARDWARE INTERFACE ---
class InverterInterface:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        # Lock ensures we don't try to read from USB twice at the same time
        self.lock = asyncio.Lock()

    def read_inverter(self, slave_id: int) -> SolarData:
        try:
            instrument = minimalmodbus.Instrument(self.port, slave_id)
            instrument.serial.baudrate = self.baudrate
            instrument.serial.timeout = 0.5
            instrument.clear_buffers_before_each_transaction = True

            # Register 0x0100: Battery SOC (%)
            soc = instrument.read_register(0x0100, 0, functioncode=3)

            # Register 0x0109: Solar Power (Watts) -> convert to kW
            solar = instrument.read_register(0x0109, 0, functioncode=3) / 1000

            # Register 0x020B: Load Power (Watts) - AC Output -> convert to kW
            load = instrument.read_register(0x020B, 0, functioncode=3) / 1000

            # Register 0x0114: Daily Generation (0.1 kWh)
            daily = instrument.read_register(0x0114, 1, functioncode=3)

            return SolarData(
                inverter_id=slave_id,
                status="online",
                battery_capacity_percentage=soc,
                solar_power_kw=solar,
                load_power_kw=load,
                daily_generation_kwh=daily
            )

        except minimalmodbus.NoResponseError:
            return SolarData(inverter_id=slave_id, status="offline (timeout)", 
                             battery_capacity_percentage=None, solar_power_kw=None, load_power_kw=None)
        except Exception as e:
            return SolarData(inverter_id=slave_id, status=f"error: {str(e)}",
                             battery_capacity_percentage=None, solar_power_kw=None, load_power_kw=None)

# Initialize Hardware & App
hardware = InverterInterface(PORT, BAUDRATE)
app = FastAPI(title="Solar Inverter API")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- API ROUTES ---

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/metrics", response_model=SystemSummary)
async def get_all_metrics():
    results = []
    
    # Lock the hardware for the duration of the scan
    async with hardware.lock:
        for inv_id in INVERTER_IDS:
            data = hardware.read_inverter(inv_id)
            results.append(data)
    
    online_units = [d for d in results if d.status == "online"]
    
    if not online_units:
        if not DEBUG:
            raise HTTPException(status_code=503, detail="No online inverters available to provide metrics")
        else:
            return SystemSummary(
            total_solar_kw=round(random.uniform(0.0, 10.0), 3),
            total_load_kw=round(random.uniform(0.0, 10.0), 3),
            avg_battery_capacity_percentage=round(random.uniform(0.0, 100.0), 1),
            total_daily_generation_kwh=round(random.uniform(0.0, 60.0), 2),
            details=results
        )

    return SystemSummary(
        total_solar_kw=sum(d.solar_power_kw for d in online_units if d.solar_power_kw is not None),
        total_load_kw=sum(d.load_power_kw for d in online_units if d.load_power_kw is not None),
        avg_battery_capacity_percentage=sum(d.battery_capacity_percentage for d in online_units if d.battery_capacity_percentage is not None) / len(online_units),
        total_daily_generation_kwh=sum(d.daily_generation_kwh for d in online_units if d.daily_generation_kwh is not None),
        details=results
    )

# --- STARTUP LOGIC ---
if __name__ == "__main__":
    # This allows you to run: python3 solar_api.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
