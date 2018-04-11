# espp

using ESP32 with MicroPython

started the wiki: will move more info there as soon I can decide which format to use

interfacing sensors:
* DHT22
* ADC: reading 5VDC or battery

interfacing peripherals:
* LED2

using MQTT:
* publish the DHT22 measures
* subscribe LED2

topics used:
* esp32/bat
* esp32/dht
* esp32/led
* esp32/status

subfolders:

## dht
* publish DHT
* working with deepsleep
## led
* subscribe LED2

## led-dht
* subscribe LED2, publish DHT

## led-dht-ds
* same with deepsleep
