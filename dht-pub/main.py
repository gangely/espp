### main.py ###
## espp dht-pub
## gea20180422

## history
# 20180422 daily error log file


### local & user parameters ###
#LOGFILE = "esperr.log"      # error log file
#sleeptime=1                # in minutes
###

no_debug()

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

### set RTC ###
from setrtc import setrtc
from machine import RTC
rtc=RTC()
t=rtc.datetime()
y=t[0]
#m=t[5]
if y==2000:
#if y==2000 or m<sleeptime:
    setrtc()

### done in dht script ###
#import machine
#rtc=machine.RTC()
#rtc.datetime()

import dht_pub

