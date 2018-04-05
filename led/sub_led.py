# sub_led.py
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
# trying deepsleep -> see sub_led_deepsleep.py
# measuring sleep consumption 130mA

from umqtt.simple import MQTTClient
from machine import Pin
from time import sleep
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


state = 0

def sub_cb(topic, msg):
    global state
    print(("message received: topic {}, message {} ".format(topic, msg)), end='')
    if msg == b"on":
        state = 1
    elif msg == b"off":
        state = 0
    elif msg == b"toggle":
        # XOR value will make it toggle
        state = state ^ 1   # use bitwise XOR
    
    print("> setting led state {}".format(state))
    led.value(state)


def main(server=SERVER):
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to {}, subscribed to {} topic".format(server, TOPIC))

    try:
        while 1:
            #micropython.mem_info()
            c.check_msg()
            print('going to sleep')
            sleep(60)
            print('waking from sleep')
            #deepsleep(10000)
    finally:
        c.disconnect()

#if __name__ == "__main__":
#    main()

main()

