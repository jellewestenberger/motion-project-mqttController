import sys
import paho.mqtt.publish as publish
import json
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import credentials
import threading
import os
hostname = "192.168.178.44"
username=credentials.username
password=credentials.password
port = 1883 



#  publish.single(topic, payload=None, qos=0, retain=False, hostname="localhost",
#     port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
#     protocol=mqtt.MQTTv311, transport="tcp")


global base_topic_switch
global motion_status

# base_topic_light = "homeassistant/light/enclosure"
# base_topic_temp = "homeassistant/sensor/enclosure_temp"
# base_topic_hum = "homeassistant/sensor/enclosure_humidity"
base_topic_switch = "homeassistant/switch/roomcam_toggle" # base mqtt topic

def on_connect(mqttc,obj, flags, rc):
    print("Connected \n rc: ",str(rc))
    # config_light=  '{"~": "%s", "name": "Enclosure", "unique_id": "enclosure_light", "cmd_t": "~/set", "stat_t": "~/state", "schema": "json", "brightness": false }' % base_topic_light
    # config_temp = u'{"~": "%s","dev_cla": "temperature", "name": "enclosure_temp", "unit_of_meas": "\N{DEGREE SIGN}C", "stat_t": "~"}' % base_topic_temp
    # config_hum = u'{"~": "%s","dev_cla": "humidity", "name": "enclosure_humidity", "unit_of_meas": "%%", "stat_t": "~"}' % base_topic_hum
    # mqttc.publish(base_topic_light+"/config",config_light,retain=True)
    # mqttc.publish(base_topic_temp+"/config",config_temp,retain=True)
    # mqttc.publish(base_topic_hum+"/config",config_hum,retain=True)    
    config_switch = u'{"~": "%s", "name": "roomcam_toggle", "stat_t": "~/state", "cmd_t": "~"}' % base_topic_switch # config payload for mqtt discovery 
    mqttc.publish(base_topic_switch+"/config",config_switch,retain=False)
def on_message(mqttc, obj, msg):
    global motion_status
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic.split("/")[-1] == 'roomcam_toggle':
        payload=msg.payload.decode('utf-8') 
        if not(motion_status) and payload == "ON":
            turn_on_motion()
        elif motion_status and payload == "OFF": 
            turn_off_motion()
               
            


def check_motion_project():
    print("check placeholder") 
    resp = os.system("if [[ $(systemctl | grep -c motion)  > 0 ]]; then echo 0 ; else echo 1 ; fi")
    resp = False 
    return resp 
        
def turn_on_motion():
    print("on placeholder") 
    os.system("sudo service motion restart ; sudo motion")

def turn_off_motion():
    print(" off placeholder") 
    os.system("sudo service motion stop")

def update_switchstate(motion_status):
    global base_topic_switch
    if motion_status:
        state = "ON"
    else:
        state= "OFF"

    mqttc.publish(base_topic_switch+"/state",'{"state": "%s"}' % state,qos=1)



def on_publish(mqttc, obj, mid):
    print("publish: \n")
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

    
mqttc=mqtt.Client()
mqttc.username_pw_set(username=username,password=password)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.connect(host=hostname,port=port)
mqttc.subscribe(base_topic_switch+"/#")
motion_status_old = check_motion_project()
# read_dht(dhtsensor,dhtpin,15,mqttc)

# mqttc.loop_forever()

while True:
    mqttc.loop()
    motion_status = check_motion_project()
    if motion_status != motion_status_old:
        update_switchstate(motion_status)
        motion_status_old = motion_status