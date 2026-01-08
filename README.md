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
WorkingDirectory=/home/pi/solar_metrics_client
# Use 'which python3' in your terminal to confirm the path to python
ExecStart=/usr/bin/python3 /home/pi/solar_metrics_client/client.py
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

