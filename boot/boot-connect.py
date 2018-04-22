### boot.py ###
## espp
## gea20180422

# This file is executed on every boot (including wake-boot from deepsleep)
# 20180222 from tuto boneskull
# 20180319 replaced pass
# 20180319 set static address
# 20180321 log retries
# 20180406 APSSID and APPASS imported from mycredentials.py
# 20180407 no_debug() call moved here
# 20180422 daily error log file

### local & user parameters ### 
STAADDR = '192.168.0.245'   ## for static address ##
STAMASK = '255.255.255.0'
STAGW   = '192.168.0.1'
STADNS  = '192.168.0.1'
LOGNAME = "esperr"          # name and ext of error log file
LOGEXT  = "log"
###

### Access Point ###
from mycredentials import MYAPSSID
from mycredentials import MYAPPASS

### misc ###
from time import sleep_ms

### RTC ###
from machine import RTC
rtc=RTC()

### set wifi in station mode ###
import network
sta_if = network.WLAN(network.STA_IF)


### connect as station ###
def connect():
    print('station active at boot:', sta_if.active())
    print('station connected at boot:', sta_if.isconnected())
    #if not sta_if.active():
        #print('activating station:', sta_if.active(True))
    if not sta_if.isconnected():
        print('connecting to network...')
        # static address
        sta_if.active(True)
        sta_if.ifconfig((STAADDR, STAMASK, STAGW, STADNS))
        # connect to AP
        sta_if.connect(MYAPSSID, MYAPPASS)
        # waiting connection + log retries
        retry = 0
        while not sta_if.isconnected():
            #pass
            t=rtc.datetime()
            retry = retry + 1
            err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} waiting connection to AP {}".format(t[0], t[1], t[2], t[4], t[5], t[6], retry))
            print(err)
            LOGFILE = ("{}-{:04d}{:02d}{:02d}.{}".format(LOGNAME, t[0], t[1], t[2], LOGEXT))
            f = open(LOGFILE, 'a')
            f.write('%s\n' %(err))
            f.close()
            #print('waiting connection')
            #print(".", end="")
            sleep_ms(10)
    # connected
    print('network config:', sta_if.ifconfig())

### no debug ###
def no_debug():
    import esp
    # this can be run from the REPL as well
    esp.osdebug(None)

no_debug()
print("osdebug set to 'None'")


