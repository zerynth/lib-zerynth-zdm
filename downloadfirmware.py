# import streams
import streams
import json

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
fw_download_link = "http://api.adm.zerinth.com/v1/workspace/wks-4pc4a2v05zpd/firmware/firm4pc4g0ex5nnm/download"
auth = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmciOiIiLCJpYXQiOjE1ODIxOTM0NTAsImlzcyI6InplcnludGgiLCJleHAiOjE1ODQ3ODU0NTAsInVpZCI6ImZfQUpld3VrVGZhd1U3VUhKMHBJQmciLCJqdGkiOiJpZjZpNTJ5OVN4Q09TSUVnQWJ6V3R3IiwibHRwIjpudWxsfQ.w6Wbhf81K4OHv_N07mElscPp979feF4wE0LpNZGYqYU"}

# use the wifi interface to link to the Access Point
# change network name, security and password as needed
print("Establishing Link...")
try:
    wifi.link(wifi_name, wifi.WIFI_WPA2, wifi_password)
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)


## let's try to connect to api.zerinth.com to download an example file
try:
    print("Trying to connect...")
    # go get that time!
    # url resolution and http protocol handling are hidden inside the requests module
    response = requests.get(fw_download_link, headers=auth)
    # let's check the http response status: if different than 200, something went wrong
    print("Http Status:",response.status)
    # if we get here, there has been no exception, exit the loop
except Exception as e:
    print(e)


try:
    # check status and print the result
    if response.status==200:
        print("Success!!")
        print("-------------")
        print("And the result is:",response.content)
        print("-------------")
except Exception as e:
    print("ooops, something very wrong! :(",e)
