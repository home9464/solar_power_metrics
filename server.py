import uvicorn
import asyncio
import minimalmodbus
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

# --- CONFIGURATION ---
PORT = '/dev/ttyACM0'
INVERTER_IDS = [1, 2] 

# Battery Constants
BATTERY_FULL_CAPACITY_KWH = 37.5  # total capacity of the battery pack
MIN_BATTERY_PERCENTAGE_USABLE = 10  # min percentage of bettery usable capacity 

class SolarData(BaseModel):
    inverter_id: int
    status: str
    battery_capacity_percentage: Optional[float] = None
    load_power_kw: Optional[float] = None
    pv_power_kw: Optional[float] = None
    battery_voltage: Optional[float] = None
    pv_power_today_kwh: Optional[float] = None

class SystemSummary(BaseModel):
    total_load_kw: float
    total_pv_kw: float
    avg_battery_capacity_percentage: float
    total_pv_today_kwh: float
    battery_full_capacity_kwh: float
    min_battery_percentage_usable: int
    details: List[SolarData]

app = FastAPI()
lock = None

@app.on_event("startup")
async def startup_event():
    global lock
    lock = asyncio.Lock()
instrument = None
try:
    instrument = minimalmodbus.Instrument(PORT, 1)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 1.0
    instrument.clear_buffers_before_each_transaction = True
except Exception as exp:
    print(exp, "only /test is OK")

def get_inverter_data(slave_id):
    if instrument is None:
        return {"status": "offline"}
    try:
        instrument.address = slave_id
        # Battery Stats
        soc = instrument.read_register(256, 0)
        time.sleep(0.1)
        # Battery Voltage
        volts = instrument.read_register(257, 0) / 10.0
        # Load Power
        time.sleep(0.1)
        load_w = instrument.read_register(539, 0) 
        # PV Power (Live) - Calc: Volts (544) * Amps (528)/10
        time.sleep(0.1)
        pv_volts = instrument.read_register(544, 0)
        time.sleep(0.1)
        pv_amps = instrument.read_register(528, 0) / 10.0
        pv_w = pv_volts * pv_amps 
        # Daily PV Generation - Using Register 566
        time.sleep(0.1)
        pv_today_raw = instrument.read_register(540, 0)
        return {
            "status": "online",
            "soc": soc,
            "volts": volts,
            "load_kw": round(load_w / 1000, 3),
            "pv_kw": round(pv_w / 1000.0, 3), 
            "pv_today_kwh": round(pv_today_raw / 100, 2) # e.g., 341 becomes 3.41
        }
    except Exception as e:
        err = f"Error reading inverter {slave_id}: {e}"
        return {"error": err}

@app.get("/metrics", response_model=SystemSummary)
async def get_all_metrics():
    results = []
    async with lock:
        for inv_id in INVERTER_IDS:
            data = get_inverter_data(inv_id)
            if data["status"] == "online":
                results.append(SolarData(
                    inverter_id=inv_id,
                    status="online",
                    battery_capacity_percentage=data["soc"],
                    load_power_kw=data["load_kw"],
                    pv_power_kw=data["pv_kw"],
                    battery_voltage=data["volts"],
                    pv_power_today_kwh=data.get("pv_today_kwh")
                ))
                await asyncio.sleep(0.2)
            else:
                results.append(SolarData(inverter_id=inv_id, status="offline"))
    online = [d for d in results if d.status == "online"]
    if not online:
        raise HTTPException(status_code=503, detail="No online inverters")
    total_load = sum(d.load_power_kw for d in online) if online else 0
    total_pv = sum(d.pv_power_kw for d in online) if online else 0
    avg_soc = (sum(d.battery_capacity_percentage for d in online) / len(online)) if online else 0
    total_pv_today = sum(d.pv_power_today_kwh for d in online if d.pv_power_today_kwh) if online else 0
    return SystemSummary(
        total_load_kw=round(total_load, 3),
        total_pv_kw=round(total_pv, 3),
        avg_battery_capacity_percentage=round(avg_soc, 1),
        total_pv_today_kwh=round(total_pv_today, 2),
        battery_full_capacity_kwh=BATTERY_FULL_CAPACITY_KWH,
        min_battery_percentage_usable=MIN_BATTERY_PERCENTAGE_USABLE,
        details=results
    )

@app.get("/test", response_model=SystemSummary)
async def get_all_metrics():
    import random
    total_load_kw = random.uniform(0, 12.0)
    total_pv_kw = random.uniform(0, 10.0)
    avg_battery_capacity_percentage = random.uniform(0, 100.0)
    total_pv_today_kwh = 23.56
    return SystemSummary(
        total_load_kw=round(total_load_kw, 1),
        total_pv_kw=round(total_pv_kw, 1),
        avg_battery_capacity_percentage=round(avg_battery_capacity_percentage, 1),
        total_pv_today_kwh=round(total_pv_today_kwh, 1),
        battery_full_capacity_kwh=BATTERY_FULL_CAPACITY_KWH,
        min_battery_percentage_usable=MIN_BATTERY_PERCENTAGE_USABLE,
        details=[]
    )

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
