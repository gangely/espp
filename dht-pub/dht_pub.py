### dht_pub.py ###
## version gea20180327

## history:
# ..
# 20180415 added client.disconnect() before going to deepsleep

### local & user parameters ### 
SERVER = '192.168.0.10'     # MQTT Server Address (Change to the IP address of your broker)
sleeptime = 4               # in minutes  
LOGFILE = "esperr.log"      # error log file
mqttretry = 3
###

### misc ###
from machine import Pin
from time import sleep
from time import sleep_ms
from machine import deepsleep
SLEEPDELAY = sleeptime * 60000 - 3000     # in milliseconds

### DHT22 ###
from dht import DHT22
sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))

### LED ###
LED2 = Pin(2, Pin.OUT)

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
#SERVER = '192.168.0.10'  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = 'ESP32_DHT22_Sensor'
TOPICDHT = b'esp32/temp_humidity'
TOPICBAT = b'esp32/battery'
TOPICSTA = b'esp32/status'
QOSDHT = 0
QOSBAT = 0
QOSSTA = 1
client = MQTTClient(CLIENT_ID, SERVER)

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


LED2.value(1)
retry = 0
while retry < mqttretry:
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
    if retry==mqttretry:
        LED2.value(0)
        err = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} failed MQTT connect, will reboot".format(t[0], t[1], t[2], t[4], t[5], t[6]))
        print(err)
        f = open(LOGFILE, 'a')
        f.write('%s\n' %(err))
        f.close()
        deepsleep(100)
LED2.value(0)

### status MQTT msg ###
LED2.value(1)
t=rtc.datetime()
sta = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} connected to MQTT socket".format(t[0], t[1], t[2], t[4], t[5], t[6]))
print(sta)
client.publish(TOPICSTA, sta, qos=QOSSTA)
LED2.value(0)

### reload rtc time ###
from setrtc import setrtc
m=t[5]
if m<sleeptime: # will reload once each hour #
    setrtc()
    t=rtc.datetime()
    tim = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} reloaded RTC time from NTP".format(t[0], t[1], t[2], t[4], t[5], t[6]))
    print(tim)
    LED2.value(1)
    client.publish(TOPICSTA, tim, qos=QOSSTA)
    LED2.value(0)

### battery measurement ###
z=rtc.datetime()
v = (adc.read()/145)+0.05
msgbat = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d},{:.2f}".format(z[0], z[1], z[2], z[4], z[5], z[6], v))
print(msgbat)
LED2.value(1)
client.publish(TOPICBAT, msgbat, qos=QOSBAT)
LED2.value(0)

### Main loop ###
while True:
#for i in range(10):
    try:
        z=rtc.datetime()
        # dht measurement
        sensor.measure()   # Poll sensor
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
            client.disconnect()
            sleep_ms(10)
            deepsleep(SLEEPDELAY)
        else:
            err1 = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} Invalid sensor readings".format(t[0], t[1], t[2], t[4], t[5], t[6]))
            print(err1)
            client.publish(TOPICSTA, err1, qos=QOSSTA)
    except OSError:
        err2 = ("{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d} Failed to read sensor".format(t[0], t[1], t[2], t[4], t[5], t[6]))
        print(err2)
        client.publish(TOPICSTA, err2, qos=QOSSTA)
    #sleep(1)
