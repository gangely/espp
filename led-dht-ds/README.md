# espp - led-dht-ds

history:
* 20180411 created a distinct script for deepsleep testing
* 20180411 more test with deepsleep; client.disconnect() solves the client.connect() problem; working on check_msg()


## problem with deepsleep

### difficulties with re-connection for mqtt client connect
* first workaround: reused mqttconnect() from sub_led_deepsleep.py, with a limited count of retries
* add client.disconnect() before deepsleep() => no more 'retry to connect'
* remaining: sometimes reboot at the first run of the script
* tried to use station.disconnect() but station.isconnected() remains True; todo: know more about sockets

### check_msg() does not catch message
* put check_msg() in a counted loop
* check_msg() does catch message while the loop is running
* message sent outside the loop are lost: where?

### output are not active during deepsleep
* software solution: ??
* HW solution: bistable circuit or device