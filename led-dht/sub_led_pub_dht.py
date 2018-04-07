# sub_led_pub_dht.py
# uses mqtt.simple
# topics esp32/led esp32/temp_humidity esp32/sta
# do process msg on/off/toggle

# history:
# example_sub_led.py adapted for ESP32; uses xor for toggle
# replaced wait_msg() by check_msg()
# added sleep() -- try 1s .. 10s
# factored out 'led.value(ledstate)'
# modifed printed info
# clarify 'global ledstate' (needed for xor function)
# auto starting main() does not work
# measuring sleep consumption
# adding code for publishing dht
# replaced 'c' by 'client'
# add print_pub_status()
# => DON'T use publishing while in callback
# 20180405 problem?? free GC is lowering by 256 at each pass
# 20180407 with deepsleep:
#   * MQTT raises sometimes (often) an OSError 118 and stops with "no AP found" message
#   * no message are found by check.msg(), even when called twice


### user definitions ###
# Default MQTT server to connect to
SERVER = "192.168.0.10"
TOPIC = b"esp32/led"
TOPICDHT = b'esp32/temp_humidity'
#TOPICBAT = b'esp32/battery'
TOPICSTA = b'esp32/status'
QOSDHT = 0
#QOSBAT = 1
QOSSTA = 0

### sleep deepsleep ###
from time import sleep
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
    #ledstate = 0
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


################
##### main #####
################


def main(server=SERVER):
    #client = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    client.set_callback(sub_cb)
    print("connecting MQTT client")     ### 20180407 with deepsleep OSError 118 after this message ###
    client.connect()
    print("subcribing to topic")
    client.subscribe(TOPIC)
    print_pub_status("Connected to {}, subscribed to {} topic".format(server, TOPIC))

    try:
        # this is the main loop #
        while 1:
            micropython.mem_info()
            # 1a. check message -> led on/off/toggle
            client.check_msg()
            # 1b. publish led status
            print_pub_status("led state is {}".format(ledstate))
            # 2. publish dht
            publish_dht()
            client.check_msg()          ### 20180407 with deepsleep, no message are found by check.msg() 
            print_pub_status("led state is {}".format(ledstate))
            # sleep
            print_pub_status('going to sleep')
            sleep(5)
            print_pub_status('waking from sleep')
            print('going to deepsleep')
            deepsleep(5000)
    finally:
        client.disconnect()

#if __name__ == "__main__":
#    main()

main()



