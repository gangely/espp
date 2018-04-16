### bat_print.py ###

BROKER='hc1'
TOPIC='esp32/battery'

import paho.mqtt.client as mqtt

# Callback fires when connected to MQTT broker.
def on_connect(client, userdata, flags, rc):
    print('Connected to', BROKER, 'with result code {0}'.format(rc))
    # Subscribe (or renew if reconnect).
    #client.subscribe('temp_humidity')
    client.subscribe(TOPIC)
    print('Subscribed to {}'.format(TOPIC))

# Callback fires when a published message is received.
def on_message(client, userdata, msg):
    # Decode temperature and humidity values from binary message paylod.
    #t,h = [float(x) for x in msg.payload.decode("utf-8").split(',')]
    #print('{0}°C {1}%'.format(t, h))
    #display_data(t, h)  # Display data on OLED display.
    message = msg.payload.decode("utf-8")
    print(message)
    #with open('espbat.log', 'a') as f:
    #    f.write('%s\n' %(message))

client = mqtt.Client()
client.on_connect = on_connect  # Specify on_connect callback
client.on_message = on_message  # Specify on_message callback
client.connect(BROKER, 1883, 60)  # Connect to MQTT broker (also running on Pi).

# Processes MQTT network traffic, callbacks and reconnections. (Blocking)
client.loop_forever()

