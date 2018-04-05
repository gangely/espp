import paho.mqtt.client as paho
import time
broker="192.168.0.10"
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published: {}, {}\n".format(userdata, result))
    pass

client1= paho.Client("control1")                    #create client object
client1.on_publish = on_publish                     #assign function to callback
client1.connect(broker,port)                        #establish connection
ret= client1.publish("esp32/led","toggle")          #publish
print(ret)                                          #print result

'''
client1.loop_start()                                #experimenting with loop

while 1:
    ret= client1.publish("esp32/led","toggle")      #publish
    print(ret)
    time.sleep(1)
'''
