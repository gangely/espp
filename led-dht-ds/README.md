# espp - led-dht-ds

history:
* 20180411 created a distinct script for deepsleep testing
* 20180411 more test with deepsleep; client.disconnect() solves the client.connect() problem; working on check_msg()
* 20180412 determined when a message is accepted

## problem with deepsleep

new version on https://github.com/gangely/espp/wiki/DeepSleep

### difficulties with re-connection for mqtt client connect
* first workaround: reused mqttconnect() from sub_led_deepsleep.py, with a limited count of retries
* add client.disconnect() before deepsleep() => no more 'retry to connect'
* remaining: sometimes reboot at the first run of the script
* tried to use station.disconnect() but station.isconnected() remains True; todo: know more about sockets

### a single check_msg() does not catch any message
* in a counted loop, check_msg() does catch message while the loop is running
* message sent outside the loop are lost: where?
* answer here:

#### when is a message accepted
* messages from a topic are accepted right after the subscription
* messages can be queued
* messages will be processed by subsequent wait_msg or check_msg
* non processed messages are lost by deepsleep
* tested with messages directly from the broker and QOS=1

#### how to use check_msg() with deepsleep
* use a time window between the subscription and check_msg
* maybe there is a solution with the broker

### output are not active during deepsleep
* software solution: ??
* HW solution: bistable circuit or device
