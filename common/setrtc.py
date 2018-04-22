### setrtc.py ###
## espp
## gea20180422 #

## history
# 20180422 daily error log file

### local & user parameters ###
LOGNAME = "esperr"          # name and ext of error log file
LOGEXT = "log"
###

### RTC ###
from machine import RTC
rtc=RTC()

### NTP ###
from ntptime import settime

### LED ###
from machine import Pin
LED2 = Pin(2, Pin.OUT)

### set RTC ###
def setrtc():
    ### settime ###
    print('setting time from NTP:')
    retry = 0
    while retry < 3:
        try:
            LED2.value(1)
            settime()
            LED2.value(0)
            break
        except OSError:
            t=rtc.datetime()
            retry = retry + 1
            err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} retry NTP settime {}".format(t[0], t[1], t[2], t[4], t[5], t[6], retry))
            print(err)
            LOGFILE = ("{}-{:04d}{:02d}{:02d}.{}".format(LOGNAME, t[0], t[1], t[2], LOGEXT))
            f = open(LOGFILE, 'a')
            f.write('%s\n' %(err))
            f.close()
            #print(".", end = "")
    t=rtc.datetime()
    print("RTC time is {:04d}{:02d}{:02d}-{:02d}{:02d}{:02d}".format(t[0], t[1], t[2], t[4], t[5], t[6]))

#setrtc()


