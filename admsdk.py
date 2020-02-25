################################################################################
# MQTT at mosquitto.org
#
# Created: 2015-10-15 21:37:25.886276
#
################################################################################

import streams
from mqtt import mqtt
from wireless import wifi
import json
import sfw

from espressif.esp32net import esp32wifi as wifi_driver

wifi_driver.auto_init()
streams.serial()

# use the wifi interface to link to the Access Point
# change network name, security and password as needed
print("Establishing Link...")
try:
    # FOR THIS EXAMPLE TO WORK, "Network-Name" AND "Wifi-Password" MUST BE SET
    # TO MATCH YOUR ACTUAL NETWORK CONFIGURATION
    wifi.link("Zerynth",wifi.WIFI_WPA2,"zerynthwifi")
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)

def is_sample(data):
    return True
    # if ('message' in data):
    #     return (data['message'].qos == 1 and data['message'].topic == "desktop/samples")
    # return False

# define MQTT callbacks
def print_sample(client, data):
    message = data['message']
    print("***** sample received: ", message.payload)
    to_send = {'key':'temp', 'value': {'temp': 24}}
    dump_to_send = json.dumps(to_send)

    client.publish(rep_topic, dump_to_send, qos=1)
    print("message published in:", rep_topic)

client_id = 'dev-4ncgqw30yiv7'
password = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYtNG5jZ3F3MzB5aXY3IiwiZXhwIjoxNjAwNTIzNzI2LCJrZXkiOjF9.CQ9nhLHGpQi5tMLRRlCHUy3XPIns-Qr1xKtdJ5xBQP8'
endpoint = 'rmq.zerinth.com'
port = 1883

# publish_topic = 'j.data.'+client_id+'.prova'

publish_topic = '.'.join(['j','data',client_id,'prova'])

sub_topic = '/'.join(['j','dn',client_id])
rep_topic = '/'.join(['j','up',client_id])
alert_topic = '/'.join(['j', 'alert', client_id])

try:

    client = mqtt.Client(client_id, clean_session= True)

    client.set_username_pw(client_id, password)

    for retry in range(10):
        try:
            # def connect(self, host, keepalive, port=PORT, ssl_ctx=None, breconnect_cb=None, aconnect_cb=None, sock_keepalive=None):
            client.connect(endpoint, 60, port)
            break
        except Exception as e:
            print("connecting...", e)
    print("connected.")

    # subscribe to channels
    client.subscribe([[sub_topic, 1]])

    client.on(mqtt.PUBLISH, print_sample, condition=is_sample)

    client.loop()

    while True:
        sleep(3000)

        x = random(0,30)
        to_send = {'temp':x}
        dump_to_send = json.dumps(to_send)

        print("pubslishing:", dump_to_send)
        print([ord(ch) for ch in dump_to_send])
        client.publish(publish_topic, dump_to_send, qos=1)

        alert = {'name':'test', 'message':'this is a test alert'}
        dump_alert = json.dumps(alert)
        print("sending alert:", dump_alert)
        client.publish(alert_topic, dump_alert, qos=1)

except Exception as e:
    print(e)