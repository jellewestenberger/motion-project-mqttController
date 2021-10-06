# Motion-project mqtt Controller
This script creates an auto-discoverable mqtt-switch for Homeassistant that allows for enabling/disabling [motion-project](https://github.com/Motion-Project/motion), a video motion monitoring tool. 

Currently only tested on Debian based hosts.

## Prequisites: 
* [motion-project](https://github.com/Motion-Project/motion) installed and configured on the same host where this script will run from.
*   A homeassistant instance with the mqtt integration installed and mqtt discovery enabled.
* An existing mqtt broker (tested with Mosquitto)
* Python 3 with paho-mqtt and psutil installed. 

## Setup:
create `hostsettings.py` containing:
```
username="mqttusername"
password="mqttpassword"
host="mqttserverIP"
port= "mqttserverPort"
```

That's it! When this script runs homeassistant will automatically discover the `switch.switchname` entity. 

## How to setup as service 
You can set up any python script as systemctl service so that it automatically runs on boot and restarts after a crash. 

First create your service file in `/etc/systemd/system/yourservice.service`

`yourservice.service` contains:

```
[Unit]
Description=motion-project mqtt controller
After=multi-user.target

[Service]
Type=simple
Restart=on-abort
ExecStart=/usr/bin/python3 <path to motionprojectmqttcontroller.py>
User=<yourhostusername> 

[Install]
WantedBy=multi-user.target
```
Reload the deamon by running `sudo systemctl daemon-reload`

Enable your service with `sudo systemctl enable yourservice.service`

Start your service with `sudo systemctl start yourservice.service`

Stop you service with `sudo systemctl stop yourservice.service`

Check the status of your service with `sudo systemctl status yourservice.service`