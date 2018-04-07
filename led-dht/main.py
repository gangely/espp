### esp led_dht ###
## main.py
## gea20180407

## history
# 20180407 no_debug() moved to boot.py

### local & user parameters ###
LOGFILE = "esperr.log"      # error log file
#sleeptime=1                # in minutes
###

#no_debug()

from time import sleep
from time import sleep_ms


### LED ###
from machine import Pin
LED2 = Pin(2, Pin.OUT)

### connect ###
LED2.value(1)
connect()
LED2.value(0)

### testing a 1s sleep after connect() to prevent further errors ###
sleep(1)
###

### set RTC if not initialised ###
from setrtc import setrtc
from machine import RTC
rtc=RTC()
t=rtc.datetime()
y=t[0]
if y==2000:
    setrtc()

### done in dht script ###
#import machine
#rtc=machine.RTC()
#rtc.datetime()

import sub_led_pub_dht

