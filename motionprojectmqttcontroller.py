import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import hostsettings
import os
import psutil
import subprocess
import time
hostname = hostsettings.host
username = hostsettings.username
password = hostsettings.password
port = hostsettings.port 

global base_topic_switch
global motion_status
update_interval = 60
entityname="roomcam_toggle"
base_topic_switch = "homeassistant/switch/"+entityname # base mqtt topic

def on_connect(mqttc,obj, flags, rc):
    print("Connected to mqtt broker. \t rc: ",str(rc))
    config_switch = u'{"~": "%s", "name": "%s", "stat_t": "~/state", "cmd_t": "~/set"}' % (base_topic_switch, entityname) # config payload for mqtt discovery 

    mqttc.publish(base_topic_switch+"/config",config_switch,retain=True)
def on_message(mqttc, obj, msg):
    global motion_status
    print("Received message: "+ msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic.split("homeassistant/switch")[-1] == '/%s/set' % entityname:
        payload=msg.payload.decode('utf-8') 
        if not(motion_status) and payload == "ON":
            turn_on_motion()
        elif motion_status and payload == "OFF": 
            turn_off_motion()
    else:
        print("Not a valid command message")
               
            

def check_motion_project(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.            
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
        
def turn_on_motion():
    print("Switching on motion-project") 
    p=subprocess.Popen("sudo service motion restart ; sudo motion",shell=True)
def turn_off_motion():
    print("Turning off motion-project") 
    os.system("sudo service motion stop")

def update_switchstate(motion_status):
    print("Updating state")
    global base_topic_switch
    if motion_status:
        state = "ON"
    else:
        state= "OFF"
    print("publishing %s to %s" %(state,base_topic_switch+"/state"))
    mqttc.publish(base_topic_switch+"/state","%s" % state,qos=1)



def on_publish(mqttc, obj, mid):
    print("Published:\t")
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
mqttc.subscribe(base_topic_switch+"/set")
motion_status_old = check_motion_project("motion")
# read_dht(dhtsensor,dhtpin,15,mqttc)
# mqttc.loop_forever()
print("Running")
seconds = time.time()
while True:
    mqttc.loop(timeout=2)
    motion_status = check_motion_project("motion")
    if motion_status != motion_status_old:
        update_switchstate(motion_status)
        motion_status_old = motion_status
    
    if (time.time()-seconds) >= update_interval:
        print("Regular update")
        update_switchstate(motion_status)
        seconds = time.time()
    
    time.sleep(1)