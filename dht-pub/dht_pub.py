### dht_pub.py ###
## version gea20180417

## history:
# ..
# 20180415 added 'client.disconnect()' before going to deepsleep
# 20180416 added 'print_pub_status()' method
#          TOPICDHT changed to esp32/dht22
# 20180417 added station.disconnect() in hope to help reconnection
#          renamed: BROKER SLEEPTIME MQTTRETRY

### local & user parameters ### 
BROKER = '192.168.0.10'     # MQTT Server Address (Change to the IP address of your broker)
SLEEPTIME = 5               # deepsleep time, in minutes  
LOGFILE = "esperr.log"      # error log file
MQTTRETRY = 3               # # of retries before rebooting
###

### misc ###
from machine import Pin
from time import sleep
from time import sleep_ms
from machine import deepsleep
SLEEPDELAY = SLEEPTIME * 60000 - 3000     # in milliseconds; edit SLEEPTIME to modify

### network ###
from network import WLAN
from network import STA_IF
station = WLAN(STA_IF)

### DHT22 ###
from dht import DHT22
sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))

### LED ###
#from machine import Pin
# ESP32 modules have blue, active-high LED on GPIO2
LED2 = Pin(2, Pin.OUT, value=0)

### ADC ###
from machine import ADC
adc = ADC(Pin(36))
#adc.atten(adc.ATTN_0DB)
adc.atten(adc.ATTN_11DB)
adc.width(adc.WIDTH_10BIT)

### RTC ###
from machine import RTC
rtc=RTC()

### LOG file ###
#LOGFILE = ("data_%s.log" %(dt))
#print("opening", LOGFILE)
#LED2.value(1)
#f = open(LOGFILE, 'w')
#f.write('%s\n' %(dt))
#f.write('dht_logpub.py\n')
#f.write('gea20180313\n')
#f.write('board ESP32-1\n')
#f.write('-------------\n')
#f.write('Date-Time,Temperature,Humidity,Voltage\n')
#f.write('YYYYDDMM-hhmm,°C,%,V\n')
#f.close()
#LED2.value(0)

### MQTT ###
from umqtt.robust import MQTTClient
#BROKER = '192.168.0.10'  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = 'ESP32_DHT22_Sensor'
TOPICDHT = b'esp32/dht22'
TOPICBAT = b'esp32/battery'
TOPICSTA = b'esp32/status'
QOSDHT = 0
QOSBAT = 0
QOSSTA = 1
client = MQTTClient(CLIENT_ID, BROKER)


###################
##### methods #####
###################


### print/publish status message ###
def print_pub_status(statusmsg):
    t=rtc.datetime()
    status = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} {}".format(t[0], t[1], t[2], t[4], t[5], t[6], statusmsg))
    print(status)
    LED2.value(1)
    client.publish(TOPICSTA, status, qos=QOSSTA)
    LED2.value(0)


##################
##### progam #####
##################

### connect to MQTT socket ###
LED2.value(1)
retry = 0
while retry < MQTTRETRY:
    try:
        client.connect()   # Connect to MQTT broker
        break
    except OSError:
        t=rtc.datetime()
        retry = retry + 1
        err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} retry MQTT connect {}".format(t[0], t[1], t[2], t[4], t[5], t[6], retry))
        print(err)
        f = open(LOGFILE, 'a')
        f.write('%s\n' %(err))
        f.close()
        #print(".", end = "")
        sleep_ms(500)
    if retry==MQTTRETRY:
        LED2.value(0)
        err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} failed MQTT connect, will reboot".format(t[0], t[1], t[2], t[4], t[5], t[6]))
        print(err)
        f = open(LOGFILE, 'a')
        f.write('%s\n' %(err))
        f.close()
        print('disconnection station...', end='')
        station.disconnect()
        sleep_ms(10)
        print('station connected:', station.isconnected())
        print('going to deepsleep')
        deepsleep(100)
LED2.value(0)

### status MQTT msg ###
'''
LED2.value(1)
t=rtc.datetime()
sta = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} connected to MQTT socket".format(t[0], t[1], t[2], t[4], t[5], t[6]))
print(sta)
client.publish(TOPICSTA, sta, qos=QOSSTA)
LED2.value(0)
'''
print_pub_status("connected to MQTT socket")

### reload rtc time each hour ###
from setrtc import setrtc
t=rtc.datetime()
m=t[5]
if m<SLEEPTIME: # will reload once each hour #
    setrtc()
    '''
    t=rtc.datetime()
    tim = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} reloaded RTC time from NTP".format(t[0], t[1], t[2], t[4], t[5], t[6]))
    print(tim)
    LED2.value(1)
    client.publish(TOPICSTA, tim, qos=QOSSTA)
    LED2.value(0)
    '''
    print_pub_status("reloaded RTC time from NTP")

### battery measurement ###
z=rtc.datetime()
v = (adc.read()/145)+0.05
msgbat = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d},{:.2f}".format(z[0], z[1], z[2], z[4], z[5], z[6], v))
print(msgbat)
LED2.value(1)
client.publish(TOPICBAT, msgbat, qos=QOSBAT)
LED2.value(0)

### loop: dht measurements and deepsleep ###
while True:
#for i in range(10):
    try:
        z=rtc.datetime()
        # dht measurement
        sensor.measure()   # Poll sensor
        #sleep_ms(1)
        #sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        if isinstance(t, float) and isinstance(h, float):  # Confirm sensor results are numeric
            msgdht = (b'{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d},{:3.1f},{:3.1f}'.format(z[0], z[1], z[2], z[4], z[5], z[6], t, h))
            print(msgdht)
            LED2.value(1)
            client.publish(TOPICDHT, msgdht, qos=QOSDHT)  # Publish sensor data to MQTT topic
            #f = open(LOGFILE, 'a')
            #f.write('%s\n' %(msg))
            #f.close()
            #sleep(1)
            LED2.value(0)
            print_pub_status("disconnecting MQTT client")
            client.disconnect()
            sleep_ms(10)
            print('disconnection station...', end='')
            station.disconnect()
            sleep_ms(10)
            print('station connected:', station.isconnected())
            print('going to deepsleep')
            deepsleep(SLEEPDELAY)
        else:
            '''
            err1 = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} Invalid sensor readings".format(t[0], t[1], t[2], t[4], t[5], t[6]))
            print(err1)
            client.publish(TOPICSTA, err1, qos=QOSSTA)
            '''
            print_pub_status("Invalid sensor readings")
    except OSError:
        '''
        err2 = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} Failed to read sensor".format(t[0], t[1], t[2], t[4], t[5], t[6]))
        print(err2)
        client.publish(TOPICSTA, err2, qos=QOSSTA)
        '''
        print_pub_status("Failed to read sensor")
    #sleep(1)
