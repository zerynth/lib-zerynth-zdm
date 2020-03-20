import zlib_zdm as zdm
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver
import streams
import json

streams.serial()

mqtt_id = 'your device id'
pwd = 'your device password'

try:
    wifi_driver.auto_init()

    for _ in range(5):
        try:
            print("connect wifi")
            wifi.link("***Wifi-name***", wifi.WIFI_WPA2, "***Wifi-password***")
            print("connect wifi done")
            break
        except Exception as e:
            print("wifi connect err", e)

    client = zdm.Thing(mqtt_id)
    client.set_password(pwd)
    client.connect()

    while True:
        sleep(1000)

except Exception as e:
    print("main", e)
