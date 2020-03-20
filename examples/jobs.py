import zlib_adm as adm
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver
import streams
import json

streams.serial()

mqtt_id = 'your device id'
pwd = 'your device password'

def custom_job_1(obj, arg):
    print("custom_job_1")
    return {
        'value 1': random(0, 100),
        'value 2': random(100, 200)
    }


def custom_job_2(obj, arg):
    print("custom_job_2")
    return 'this is an example result'


# you can call job1 and job2 method using rpc
my_jobs = {
    'job1': custom_job_1,
    'job2': custom_job_2,
}

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

    client = adm.Thing(mqtt_id, job_list=my_jobs)
    client.set_password(pwd)
    client.connect()

    while True:
        sleep(1000)

except Exception as e:
    print("main", e)
