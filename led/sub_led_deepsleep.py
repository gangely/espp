# sub_led_deepsleep.py
# uses mqtt.simple
# topic esp32/led
# process msg on/off/toggle
# history:
# example_sub_led.py adapted for ESP32; uses xor for toggle
# replaced wait_msg() by check_msg()
# added sleep() -- try 1s .. 10s
# factored out 'led.value(state)'
# modifed printed info
# clarify 'global state' (needed for xor function)
# auto starting main() does not work
# trying deepsleep -> OSerror 118 from umqtt.simple.connect()
# mqttconnect() with mqttretry=5 -> will connect with sometimes retries
# experimenting with led: 
#   * with 1 check_msg, message in not acquired
#   * LED2 switch off when entering deepsleep

from umqtt.simple import MQTTClient
from machine import Pin
from time import sleep
from time import sleep_ms
from machine import deepsleep
import ubinascii
import machine
import micropython


# ESP32 modules have blue, active-high LED on GPIO2, replace
# with something else if needed.
led = Pin(2, Pin.OUT, value=0)

# Default MQTT server to connect to
SERVER = "192.168.0.10"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
print(CLIENT_ID)
TOPIC = b"esp32/led"
mqttretry = 5

state = 0

def sub_cb(topic, msg):
    global state
    print(("message received: topic {}, message {}, ".format(topic, msg)), end='')
    if msg == b"on":
        state = 1
    elif msg == b"off":
        state = 0
    elif msg == b"toggle":
        # XOR value will make it toggle
        state = state ^ 1   # use bitwise XOR
    
    print("> setting led state {}".format(state))
    led.value(state)

c = MQTTClient(CLIENT_ID, SERVER)

def mqttconnect():
    global mqttretry
    retry=0
    while retry < mqttretry:
        try:
            c.connect()   # Connect to MQTT broker
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
            deepsleep(1000)

def main(server=SERVER):
    #c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    #c.connect()
    mqttconnect()
    c.subscribe(TOPIC)
    print("Connected to {}, subscribed to {} topic".format(server, TOPIC))

    try:
        while 1:
            #micropython.mem_info()
            c.check_msg()
            sleep(5)
            if state == 1:
                print('going to deepsleep')
                deepsleep(10000)
    finally:
        c.disconnect()

#if __name__ == "__main__":
#    main()

main()

