import streams
import json
from mqtt import mqtt

# import the wifi interface
from wireless import wifi

# import the http module
import requests
from espressif.esp32net import esp32wifi as wifi_driver

streams.serial()
wifi_driver.auto_init()

wifi_name = "Zerynth"
wifi_password = "zerynthwifi"
# fw_download_link = "http://api.adm.zerinth.com/v1/workspace/wks-4pc4a2v05zpd/firmware/firm4pc4g0ex5nnm/download"
auth = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmciOiIiLCJpYXQiOjE1ODIxOTM0NTAsImlzcyI6InplcnludGgiLCJleHAiOjE1ODQ3ODU0NTAsInVpZCI6ImZfQUpld3VrVGZhd1U3VUhKMHBJQmciLCJqdGkiOiJpZjZpNTJ5OVN4Q09TSUVnQWJ6V3R3IiwibHRwIjpudWxsfQ.w6Wbhf81K4OHv_N07mElscPp979feF4wE0LpNZGYqYU"}

device_id = "dev-4pnefulyx2bn"
client_id = "dev-4pnefulyx2bn"
password  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtNHBuZWZ1bHl4MmJuIiwidXNlciI6ImRldi00cG5lZnVseXgyYm4iLCJleHAiOjE5MTYyMzkwMjIsImtleSI6MX0.8Pi1y0s22ij1No-7oPysKGtpW0_ec7MMuZ3O5HeKqWw"
broker    = "rmq.adm.zerinth.com"

subscribe_topic = '/'.join(['j','dn',device_id])
publish_topic = '/'.join(['j', 'up', device_id])
data_topic = '/'.join(['j','data', device_id,'ufficio'])

# use the wifi interface to link to the Access Point
# change network name, security and password as needed
print("Establishing Link...")
try:
    wifi.link(wifi_name, wifi.WIFI_WPA2, wifi_password)
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)

# define MQTT callbacks
def is_fota_response(data):
    message = data['message']
    body = json.loads(message.payload)
    if body["key"] == "#fota_info":
        return True
    return False

def is_status(data):
    message = data['message']
    body = json.loads(message.payload)
    if body["key"] == "#status":
        return True
    return False

def process_fota(client,data):
    try:
        message = data['message']
        print("FOTA info: ", message.payload)
        print("\n")
    except Exception as e:
        print("An error occurred: ",e)

def process_status(client,data):
    try:
        message = data['message']
        body = json.loads(message.payload)
        print("Status received: ", body)
    except Exception as e:
        print("error taking message payload: ", e)

    try:
        if body["value"] != None:
            current, current_fw = None
            expected, expected_fw = None

            value = body["value"]

            if value["current"] != None:
                current = json.loads(value["current"])
                current = current["status"]
                if current["fw_version"] != None:
                    current_fw = current["fwversion"]

            if value["expected"] != None:
                expected = json.loads(value["expected"])
                expected = expected["status"]
                if expected["fw_version"] != None:
                    expected_fw = expected["fwversion"]

            # The device has to download a new firmware
            if ((expected_fw != None) and (expected_fw != current_fw)):
                payload = {
                    "key": "#fw_version",
                    "value": {
                        "fota_info": {
                            "fw_version": expected_fw,
                            "progress": "accepted"
                        }
                    }
                }
                client.publish(publish_topic, json.dumps(payload), qos=1)
    except Exception as e:
        print("error taking value object from payload: ", e)


try:
    client = mqtt.Client(client_id, True)
    client.set_username_pw(device_id, password)

    try:
        client.connect(broker, 60)
    except Exception as e:
        print("connecting...")

    print("connected.")
    # subscribe to channels
    client.subscribe([[subscribe_topic, 1]])
    print("Subscribed to topic: ", subscribe_topic)
    client.on(mqtt.PUBLISH, process_fota, is_fota_response)
    client.on(mqtt.PUBLISH, process_status, is_status)
    client.loop()

    sleep(2000)

    # The device ask the ADM its current and expected status
    payload2 = {"key": "#status", "value": {}}
    client.publish(publish_topic, json.dumps(payload2), qos=1)
    print("Status request published to topic: " + publish_topic)

    try:
        while True:
            payload = {"key": "#fota_info", "value": {"fw_version": "1.1"}}
            client.publish(publish_topic, json.dumps(payload))
            print("Payload: ", payload, " published to: ", publish_topic)
            sleep(5000)
    except Exception as e:
        print("error: ", e)

    while True:
        sleep(100000)
        temp = random(19,23)
        pressure = random(50, 60)
        humidity = random(60, 75)
        payload = {"temp": temp, "pressure": pressure, "humidity": humidity}
        client.publish(data_topic, json.dumps(payload), qos=1)
        print("Data published to topic: " + data_topic)
except Exception as e:
    print("an error occurred ",e)
