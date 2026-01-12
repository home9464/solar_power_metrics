# Monitor the solar metrics

1. Current solar panel generated power
2. Current load consumed power
3. battery capacity remaining percentage

# Hardware 

- A pi4 board, worked as server, to connect to solar hybrid inverter via USB-RS485 cable, read data from it the expose the data by 
at http://0.0.0.0:8000/metrics


- A pi2w board, workded as a client, to read the metrics from http://0.0.0.0:8000/metrics then display it on a 7 segment display

# Software


# Server

## 1. add user to dialout so we can read USB-RS485 signal 
```bash
sudo usermod -a -G dialout $USER
```

## 2. Create a system servce to read signal

```bash
sudo nano /etc/systemd/system/solar.service
```

## 3. Copy & Paste to above file
```bash
[Unit]
Description=7-Segment PST Solar Service
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
# This is critical for libraries to load
Environment=PYTHONPATH=/home/ubuntu/.local/lib/python3.8/site-packages
WorkingDirectory=/home/ubuntu/solar_metrics_server
ExecStart=/usr/bin/python3 /home/ubuntu/solar_metrics_server/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 4. Save & Exit

Press Ctrl + O then Enter to save, and Ctrl + X to exit.


## 5. Start it
```bash
sudo systemctl enable solar.service
sudo systemctl start solar.service
```

## 6. edit it if needed
```bash
sudo systemctl edit --full solar.service
```



# Client

## 1. Create a system servce to read metrics from server
```bash
git clone https://github.com/home9464/solar_power_metrics.git
pip install luma.led-matrix --break-system-packages
sudo nano /etc/systemd/system/solar_metrics_client.service
```

## 2. Copy & Paste

```bash
[Unit]
Description=7-Segment PST Solar Service
After=network-online.target
Wants=network-online.target

[Service]
# Ensure this matches your actual username
User=pi
# Adjust the path to where your site-packages actually live
Environment=PYTHONPATH=/home/pi/.local/lib/python3.11/site-packages
WorkingDirectory=/home/pi/solar_power_metrics
# Use 'which python3' in your terminal to confirm the path to python
ExecStart=/usr/bin/python3 /home/pi/solar_power_metrics/client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 3. Save & Exit

Press Ctrl + O then Enter to save, and Ctrl + X to exit.

## 4. Start it

```bash
sudo systemctl enable solar_metrics_client
sudo systemctl start solar_metrics_client
```

## 5. edit it if needed
```bash
sudo systemctl edit --full solar_metrics_client
```


the server returns a dict 

{
            "status": "online",
            "soc": soc,
            "volts": volts,
            "load_kw": round(load_w / 1000, 3),
            "pv_kw": round(pv_w / 100, 3), 
            "pv_today_kwh": round(pv_today_raw / 10, 2) # e.g., 341 becomes 34.1
        }

for each inverter. we have two interters. now I want the client shows "useable time" based on current battery capacity and current load_kw. The battery has a capacity of 37.5kwh, and the inverter will shutdown when the battery capacity is below 10%.

so the client should calculate the useable time based on the current battery capacity and current load_kw. and show it on the display.

it should alternatively show current content and the new (batter_percentage useable_time). batter_percentage occupy 2 digits. follow by space. then useable_time occupy 5 digits to show hhh.mm (hours and mins left before depletion)
it could show 5.40 for 5 hrs 40mins or 500.15 for 500 hrs 15 mins.




## Reference

```
#################################################################################################################################
#                                   MODBUS
#################################################################################################################################

modbus:
  - name: modbus_tcp
    type: rtuovertcp
    host: 192.168.1.30
    port: 8888
    sensors:
#Load active power phase A
      - name: Modbus_Inverter_Power
        unit_of_measurement: W
        scale: 1
        slave: 1
        address: 539
        input_type: holding
        
#Battery level percentage
      - name: Modbus_Inverter_BatteryLevel
        unit_of_measurement: '%'
        scale: 1
        slave: 1
        address: 256
        input_type: holding

#Last equalizing charge completion time
      - name: Modbus_Inverter_BatteryLastEqualization
        scale: 1
        slave: 1
        address: 61507
        input_type: holding


#Battery voltage
      - name: Modbus_Inverter_BatteryV
        unit_of_measurement: V
        scale: 0.1
        precision: 1
        slave: 1
        address: 257
        input_type: holding
        
#PV panel 1 voltage 
      - name: Modbus_Inverter_PV_voltage
        unit_of_measurement: V
        scale: 0.1
        precision: 1
        slave: 1
        address: 263
        input_type: holding
        
#PV panel 1 current 
      - name: Modbus_Inverter_PV_current
        unit_of_measurement: A
        scale: 0.1
        precision: 1
        slave: 1
        address: 264
        input_type: holding
        
#PV panel 1 power
      - name: Modbus_Inverter_PV_power
        unit_of_measurement: W
        scale: 1
        slave: 1
        address: 265
        input_type: holding
        
#Total charge power, include charge power by mains and pv
      - name: Modbus_Inverter_Charge_power
        unit_of_measurement: W
        scale: 1
        slave: 1
        address: 270
        input_type: holding
        
#Charge state
      - name: Modbus_Inverter_battery_chargestate
        scale: 1
        slave: 1
        address: 267
        input_type: holding

#Current state of the machine
      - name: Modbus_Inverter_Operation
        scale: 1
        slave: 1
        address: 528
        input_type: holding

#Load side current phase A
      - name: Modbus_Inverter_current
        unit_of_measurement: A
        scale: 0.1
        precision: 1
        slave: 1
        address: 537
        input_type: holding
        
#Battery side current when charging on mains
      - name: Modbus_Inverter_Main_charge_current
        unit_of_measurement: A
        scale: 0.1
        precision: 1
        slave: 1
        address: 542
        input_type: holding
        
#Battery side current by PV charging
      - name: Modbus_Inverter_PV_charge_current
        unit_of_measurement: A
        scale: 0.1
        precision: 1
        slave: 1
        address: 548
        input_type: holding

#The total PV power generation of the day, applicable to the 2nd generation machines
      - name: Modbus_Inverter_pv_daily_consumption
        unit_of_measurement: kWh
        scale: 0.1
        precision: 1
        slave: 1
        address: 61487
        input_type: holding

#The total battery charge level (AH) of the day
      - name: Modbus_Inverter_battery_charge_daily
        unit_of_measurement: Ah
        scale: 1
        slave: 1
        address: 61485
        input_type: holding

#The total battery discharge level (AH) of the day
      - name: Modbus_Inverter_battery_discharge_daily
        unit_of_measurement: Ah
        scale: 1
        slave: 1
        address: 61486
        input_type: holding

#The total PV power generation of the day
      - name: Modbus_Inverter_pv_daily_consumption
        unit_of_measurement: kWh
        scale: 0.1
        precision: 1
        slave: 1
        address: 61487
        input_type: holding

#The total power consumption by load of the day
      - name: Modbus_Inverter_load_daily_consumption
        unit_of_measurement: kWh
        scale: 0.1
        precision: 1
        slave: 1
        address: 61485
        input_type: holding
        
#Total running days
      - name: Modbus_Inverter_uptime
        unit_of_measurement: days
        scale: 1
        slave: 1
        address: 61489
        input_type: holding
 
#Accumulated PV power generation
      - name: Modbus_Inverter_PV_Generated
        unit_of_measurement: kWh
        state_class: total_increasing
        scale: 0.1
        precision: 1
        slave: 1
        address: 61496
        input_type: holding
 
#Power consumption by load from mains of today
      - name: Modbus_Inverter_Main_load_power_daily
        unit_of_measurement: kWh
        scale: 0.1
        precision: 1
        slave: 1
        address: 61501
        input_type: holding

#DC-DC heat sink temperature
      - name: Modbus_Inverter_DCDC_temp
        unit_of_measurement: '°C'
        scale: 0.1
        precision: 1
        slave: 1
        address: 544
        input_type: holding

#DC-AC heat sink temperature
      - name: Modbus_Inverter_DCAC_temp
        unit_of_measurement: '°C'
        scale: 0.1
        precision: 1
        slave: 1
        address: 545
        input_type: holding

#Translator heat sink tmperature
      - name: Modbus_Inverter_translator_temp
        unit_of_measurement: '°C'
        scale: 0.1
        precision: 1
        slave: 1
        address: 546
        input_type: holding
        
#Load percentage phase A
      - name: Modbus_Inverter_LoadRatio
        unit_of_measurement: '%'
        scale: 1
        slave: 1
        address: 543
        input_type: holding
```