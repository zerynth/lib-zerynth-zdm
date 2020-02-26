# import streams
import streams
import json
from mqtt import mqtt

# import the wifi interface
from wireless import wifi

# import the http module
import requests
from espressif.esp32net import esp32wifi as wifi_driver

streams.serial()
# init the wifi driver!
# The driver automatically registers itself to the wifi interface
# with the correct configuration for the selected board
wifi_driver.auto_init()

wifi_name = "Zerynth"
wifi_password = "zerynthwifi"
# fw_download_link = "http://api.adm.zerinth.com/v1/workspace/wks-4pc4a2v05zpd/firmware/firm4pc4g0ex5nnm/download"
auth = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmciOiIiLCJpYXQiOjE1ODIxOTM0NTAsImlzcyI6InplcnludGgiLCJleHAiOjE1ODQ3ODU0NTAsInVpZCI6ImZfQUpld3VrVGZhd1U3VUhKMHBJQmciLCJqdGkiOiJpZjZpNTJ5OVN4Q09TSUVnQWJ6V3R3IiwibHRwIjpudWxsfQ.w6Wbhf81K4OHv_N07mElscPp979feF4wE0LpNZGYqYU"}

device_id = "dev-4pcidr47kutt"
client_id = "dev-4pcidr47kutt"
password  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtNHBjaWRyNDdrdXR0IiwidXNlciI6ImRldi00cGNpZHI0N2t1dHQiLCJleHAiOjE5MTYyMzkwMjIsImtleSI6MX0.wcMkmJGvHLz5juaL9scUpv9PKsMWdXMh_5oCbkGckCA"
broker    = "rmq.adm.zerinth.com"

topic = "j/dn/" + device_id
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
def is_fota(data):
    message = data['message']
    body = json.loads(message.payload)
    if body["key"] == "fota":
        return True
    return False

def process_fota(client,data):
    try:
        message = data['message']
        body = json.loads(message.payload)
        value = (body["value"])
        fw_download_link = value["url"]
        ## connect to api.adm.zerinth.com to download the firmware
        print("Trying to connect...")
        response = requests.get(fw_download_link, headers=auth)
        # let's check the http response status: if different than 200, something went wrong
        print("Http Status:",response.status)
        # check status and print the result
        if response.status==200:
            print("Firmware downloaded successfully.")
            print("-------------")
            print("Version: ", value["version"])
            print("-------------")
            print("File content:")
            print(response.content)
            print("-------------")
    except Exception as e:
        print("An error occurred: ",e)

try:
    client = mqtt.Client(client_id, True)
    client.set_username_pw(device_id, password)
    for retry in range(10):
        try:
            client.connect(broker, 60)
            break
        except Exception as e:
            print("connecting...")
    print("connected.")
    # subscribe to channels
    client.subscribe([[topic, 1]])
    print("Subscribed to topic: ", topic)
    client.on(mqtt.PUBLISH, process_fota, is_fota)
    client.loop()

except Exception as e:
    print("an error occurred ",e)
