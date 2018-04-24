### pub_led_loop.py ###
## espp/led /led-dht /led-dht-ds
## gea20180424

## history
# 20180424 parameters BROKER ..


## user and local parameters ##
BROKER = "hc1"
PORT = 1883
TOPIC = "esp32/led"
QOS = 1
RETAIN = True
## not used
#user = "yourUser"
#password = "yourPassword"


import paho.mqtt.client as mqttClient
import time

 
def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
 
        print("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
 
        print("Connection failed")
 
Connected = False   #global variable for the state of the connection
  
client = mqttClient.Client("Python")                #create new instance
#client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                       #attach function to callback
client.connect(BROKER, port=PORT)                   #connect to broker
 
client.loop_start()        #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)
 
try:
    while True:
 
        value = input('Enter the message: ')
        client.publish(TOPIC,value,qos=QOS,retain=RETAIN)
 
except KeyboardInterrupt:
 
    client.disconnect()
    client.loop_stop()
