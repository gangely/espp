# espp - led-dht

history:
* 20180410 summary


## problem with deepsleep

moved to led-dht-ds

* difficulties with re-connection for mqtt client connect => workaround with mqtt-connect()
* check-msg() does not catch any message
* output are not active during deepsleep