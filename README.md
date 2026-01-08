# Server

```bash
sudo usermod -a -G dialout $USER
```

```bash
sudo nano /etc/systemd/system/solar.service
```

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
ExecStart=/usr/bin/python3 /home/ubuntu/solar_power_metrics/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Start it
```bash
sudo systemctl restart solar.service
```

## 5. edit it if needed
```bash
sudo systemctl edit --full solar.service
```



# Client

## 1. create a service script
```bash
sudo nano /etc/systemd/system/solar_metrics_client.service
```

## 2. copy & paste

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
sudo systemctl restart solar_metrics_client
```

## 5. edit it if needed
```bash
sudo systemctl edit --full solar.service
```

