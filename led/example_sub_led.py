from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython


# ESP32 modules have blue, active-high LED on GPIO2, replace
# with something else if needed.
led = Pin(2, Pin.OUT, value=1)

# Default MQTT server to connect to
SERVER = "192.168.0.10"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"esp32/led"


state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(1)
        state = 1
    elif msg == b"off":
        led.value(0)
        state = 0
    elif msg == b"toggle":
        # XOR value will make it toggle
        state = state ^ 1   # use bitwise XOR
        led.value(state)


def main(server=SERVER):
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))

    try:
        while 1:
            #micropython.mem_info()
            c.wait_msg()
    finally:
        c.disconnect()
