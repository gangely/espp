### sub_led_pub_dht_ds.py
## project espp/led-dht-ds
## gea20180423
# further development with deepsleep
# uses mqtt.simple
# topics esp32/led esp32/temp_humidity esp32/sta
# do process msg on/off/toggle

## history:
# example_sub_led.py adapted for ESP32; uses xor for toggle
# replaced wait_msg() by check_msg()
# added sleep() -- try 1s .. 10s
# factored out 'led.value(ledstate)'
# modifed printed info
# declaring 'global ledstate' seems needed for xor function
# auto starting main() does not work; simply calling main() is ok
# measuring sleep consumption 130 mA
# adding code for publishing dht
# replaced 'c' by 'client'
# add print_pub_status()
# => DON'T use publishing while in callback
# 20180405 problem?? free GC is lowering by 256 at each pass
# 20180407 with deepsleep:
#        * MQTT raises sometimes (often) an OSError 118 and stops with "no AP found" message
#        * no message are found by check.msg(), even when called twice; ok with wait_msg()
# 20180407 added mqtt_connect() to catch OSError 118; observing up to 4 retries
# 20180410 publish 'connected' message
# 20180410 mqtt_connect(): with a 100ms sleep, # retries is down to 1  
# 20180410 check_msg() does not work more by placing it after publish
# 20180411 disconnecting before deepsleep
#        * client.disconnect() has a positive effect: at first, no more retry of mqtt_connect(), except when restarting the script !!
#        * station.disconnect() seems to have no effect: station.isconnected() reports True ??
# 20180411 reuse mqttconnect() from sub_led_deepsleep.py (with limited count)
# 20180411 more test with check.msg() in a counted loop: messages sent before the loop are not catched
# 20180412 use wait(testpoint) to determine when a message is accepted
#        * messages from a topic are accepted right after the subscription
#        * messages can be queued
#        * messages will be processed by subsequent wait_msg or check_msg
#        * non processed messages are lost by deepsleep
# 20180423 edited TOPICDHT; replaced TOPICLED
#        * broker set with persistence => suppress some wait(), change timing, remove mem_info

### user definitions ###
# Default MQTT server to connect to
SERVER = "192.168.0.10"
TOPICLED = b"esp32/led"
TOPICDHT = b'esp32/dht22'
#TOPICBAT = b'esp32/battery'
TOPICSTA = b'esp32/status'
QOSDHT = 0
#QOSBAT = 1
QOSSTA = 0

# Other
mqttretry = 3

### sleep deepsleep ###
from time import sleep
from time import sleep_ms
from machine import deepsleep

### CLIENT_ID ###
import ubinascii
import machine
import micropython
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
print("MQTT client ID is {}".format(CLIENT_ID))

### LED ###
from machine import Pin
# ESP32 modules have blue, active-high LED on GPIO2
led = Pin(2, Pin.OUT, value=0)

### network ###
from network import WLAN
from network import STA_IF
station = WLAN(STA_IF)

### MQTT ###
from umqtt.simple import MQTTClient
client = MQTTClient(CLIENT_ID, SERVER)

### DHT22 ###
from dht import DHT22
sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))

### RTC ###
from machine import RTC
rtc=RTC()


###################
##### methods #####
###################


### print/publish status message ###
def print_pub_status(statusmsg):
    print(statusmsg)
    client.publish(TOPICSTA, statusmsg, qos=QOSSTA)


### message callback to set led state ###
ledstate = 0
def sub_cb(topic, msg):
    global ledstate
    print(("message received: topic {}, message {} ".format(topic, msg)), end='')
    if msg == b"on":
        ledstate = 1
    elif msg == b"off":
        ledstate = 0
    elif msg == b"toggle":
        # XOR value will make it toggle
        ledstate = ledstate ^ 1   # use bitwise XOR
    print(">> setting led ledstate {}".format(ledstate))
    led.value(ledstate)


### mqtt connect with retry ###
'''
def mqtt_connect():
    CONNECT=1
    print("connecting as MQTT client")     ### 20180407 with deepsleep OSError 118 after this message ###
    while CONNECT != 0:
        try:
            client.connect()
            CONNECT=0
            print_pub_status("connected as MQTT client")
        except OSError:
            print("retrying connect {}".format(CONNECT))
            CONNECT=CONNECT+1
            sleep_ms(100)
'''

def mqtt_connect():
    global mqttretry
    retry=0
    print("connecting as MQTT client")
    while retry < mqttretry:
        try:
            client.connect()   # Connect to MQTT broker
            print_pub_status("connected as MQTT client")
            break
        except OSError:
            #t=rtc.datetime()
            retry = retry + 1
            #err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} retry MQTT connect {}".format(t[0], t[1], t[2], t[4], t[5], t[6], retry))
            #print(err)
            print("retry MQTT connect {}".format(retry))
            #f = open(LOGFILE, 'a')
            #f.write('%s\n' %(err))
            #f.close()
            #print(".", end = "")
            sleep_ms(500)
        if retry==mqttretry:
            #LED2.value(0)
            #err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} failed MQTT connect, will reboot".format(t[0], t[1], t[2], t[4], t[5], t[6]))
            err = ("failed MQTT connect, will reboot")
            print(err)
            #f = open(LOGFILE, 'a')
            #f.write('%s\n' %(err))
            #f.close()
            print('disconnecting')
            station.disconnect()
            sleep_ms(100)
            print('station connected:', station.isconnected())
            print('going to deepsleep')
            deepsleep(1000)


### publish dht ###
def publish_dht():
    DHTOK=0
    while DHTOK == 0:
        try:
            #z=rtc.datetime()
            # dht measurement
            sensor.measure()   # Poll sensor
            t = sensor.temperature()
            h = sensor.humidity()
            if isinstance(t, float) and isinstance(h, float):  # Confirm sensor results are numeric
                msgdht = (b'{:3.1f},{:3.1f}'.format(t, h,))
                #msgdht = (b'{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d},{:3.1f},{:3.1f}'.format(z[0], z[1], z[2], z[4], z[5], z[6], t, h))
                print(msgdht)
                #LED2.value(1)
                client.publish(TOPICDHT, msgdht, qos=QOSDHT)  # Publish sensor data to MQTT topic
                #f = open(LOGFILE, 'a')
                #f.write('%s\n' %(msg))
                #f.close()
                #sleep(1)
                #LED2.value(0)
                #deepsleep(SLEEPDELAY)
                DHTOK=1
            else:
                print_pub_status("Invalid sensor readings")
                #err1 = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} Invalid sensor readings".format(t[0], t[1], t[2], t[4], t[5], t[6]))
                #print(err1)
                #client.publish(TOPICSTA, err1, qos=QOSSTA)
        except OSError:
            print_pub_status("Failed to read sensor")
            #err2 = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} Failed to read sensor".format(t[0], t[1], t[2], t[4], t[5], t[6]))
            #print(err2)
            #client.publish(TOPICSTA, err2, qos=QOSSTA)


### waiting for test ###
def wait(testpoint):
    print('waiting 30s after {}...'.format(testpoint), end='')
    sleep(30)
    print('done')


################
##### main #####
################


def main(server=SERVER):
    print('station connected:', station.isconnected())
    #wait('station connected')
    #client = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    client.set_callback(sub_cb)
    #print("connecting MQTT client")     ### 20180407 with deepsleep OSError 118 after this message ###
    #client.connect()
    mqtt_connect()
    #wait('mqtt connected')
    print("subcribing to topic")
    client.subscribe(TOPICLED)
    print_pub_status("Connected to {}, subscribed to {} topic".format(server, TOPICLED))
    #wait('subscribed to topic') 
    try:
        # this is the main loop #
        while 1:
            #micropython.mem_info()
            # 1. publish dht
            publish_dht()
            # 2. check message -> led on/off/toggle
            #print("waiting message")
            #client.wait_msg()
            print_pub_status('checking message')
            #count = 0
            #while count < 15:
            client.check_msg()          ### 20180407 with deepsleep, no message are found by check.msg()
            #    print('.', end='')
            #    sleep(1)
            #    count=count+1
            #print('\r')
            # 3. publish led status
            print_pub_status("led state is {}".format(ledstate))
            wait('led change')
            print_pub_status('disconnecting client')
            client.disconnect()
            sleep(1)
            #while station.isconnected() == True:
            print('disconnection station...', end='')
            station.disconnect()
            sleep(1)
            print('station connected:', station.isconnected())
            print('going to deepsleep')
            deepsleep(30000)
    finally:
        client.disconnect()
        print('station connected:', station.isconnected())

#if __name__ == "__main__":
#    main()

main()



