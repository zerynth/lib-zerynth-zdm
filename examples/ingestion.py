import zlib_adm as adm
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver
import streams
import json

streams.serial()

mqtt_id = 'your device id'
pwd = 'your device password'


def pub_random():
    print('------ publish random ------')
    tags = ['tag1', 'tag2', 'tag3']
    payload = {
        'value': 0
    }

    for t in tags:
        payload['value'] = random(0, 100)
        client.publish(json.dumps(payload), t)
        print('published on tag:', t, ':', payload)

    print('pub_random done')


def pub_temp_pressure():
    print('---- publish temp_pressure ----')
    tag = 'tag4'
    temp = random(19, 23)
    pressure = random(50, 60)
    payload = {'temp': temp, 'pressure': pressure}
    client.publish(json.dumps(payload), tag)
    print('published on tag: ', tag, ':', payload)


try:
    wifi_driver.auto_init()
    for _ in range(5):
        try:
            print("connect wifi")
            # Write here your Wifi SSID and password
            wifi.link("***Wifi-name***", wifi.WIFI_WPA2, "***Wifi-password***")
            print("connect wifi done")
            break
        except Exception as e:
            print("wifi connect err", e)

    client = adm.Thing(mqtt_id)
    client.set_password(pwd)
    client.connect()

    while True:
        sleep(5000)
        pub_random()
        pub_ufficio()

except Exception as e:
    print("main", e)

