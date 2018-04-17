# espp

using ESP32 with MicroPython

* please find on this page a brief description of the subfolders
* see more notes in each of the subfolders README and in the [wiki pages](https://github.com/gangely/espp/wiki/) 

## [boot](boot)
* boot.py  (definition of `connect()`, used in all subprojects)

## [common](common)
* setrtc.py, used in all subprojects

## [dht-pub](dht-pub)
* subproject: publishing DHT22, battery, status
* works with deepsleep

## led
* subproject: subscribe LED2

## led-dht
* subproject: subscribe LED2, publish DHT22

## [led-dht-ds](led-dht-ds)
* subproject: same with deepsleep
