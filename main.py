# zlib adm
# Created at 2020-02-21 07:27:44.506933

import zlib_adm as adm
import mcu
from wireless import wifi
import sfw
from espressif.esp32net import esp32wifi as wifi_driver
import streams
import json
import vm
import random

client = None

streams.serial()

# uncomment this line if you don't use a 4ZeroBox
sfw.watchdog(0, 120000)

mqtt_id = 'dev-4py3x1xk2rkf'
pwd = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtNHB5M3gxeGsycmtmIiwidXNlciI6ImRldi00cHkzeDF4azJya2YiLCJrZXkiOjEsImV4cCI6MjUxNjIzOTAyMn0.a3H6XTmRRMAb0f1P6p4R9xyCZx4XiELbE18qJce07z0'


def custom_job_1(obj, arg):
    print("custom_job_1")
    print("arg:", arg)
    return {
        'value 1': random(0, 100),
        'value 2': random(100, 200)
    }


def custom_job_2(obj, arg):
    print("custom_job_2")
    print("arg:", arg)
    return 'this is an example result'


# you can call job1 and job2 method using rpc
my_jobs = {
    'job1': custom_job_1,
    'job2': custom_job_2,
}


def callback_update_status(obj, new_status):
    print("callback update status")
    print("new_status:", new_status)


def callback_accept_fota(fota_data):
    print("callback accept fota")
    print("fota data:", fota_data)
    return True


def clear_st(key):
    client.clear_status_key(key)


def pub_random():
    print("------ publish rnd ------")
    tags = [None, 'tag1', 'tag2', 'tag3']
    payload = {
        'topic': None,
        'value': 0
    }
    for t in tags:
        payload['tag'] = t
        payload['value'] = random(0, 100)
        client.publish(json.dumps(payload), t)

        print(t, ':', payload)
    print("done")
    print(" ")


def pub_ufficio():
    print("---- publish ufficio ----")
    temp = random(19, 23)
    pressure = random(50, 60)
    payload = {"temp": temp, "pressure": pressure}
    print(payload)
    client.publish(json.dumps(payload), 'ufficio')
    print("done")
    print(" ")


def req_status():
    print("------ req. status ------")
    client.request_status()
    print("done")
    print(" ")


def print_current():
    print(client.current)


def print_expected():
    print(client.expected)


tags = ["caffe", "cibo", "bevande", "armadi",
        "case", "tutto"]  # tags where to publish
names = ["prova1", "prova2", "prova3", "prova4"]

try:
    wifi_driver.auto_init()
    for _ in range(5):
        try:
            print("connect wifi")
            wifi.link("Zerynth", wifi.WIFI_WPA2, "zerynthwifi")
            print("connect wifi done")
            break
        except Exception as e:
            print("wifi connect err", e)

    client = adm.Thing(mqtt_id, rpc=my_jobs)
    client.set_password(pwd)
    client.connect()
    asd = vm.info()

    while True:
        sleep(5000)
        pub_random()
        pub_ufficio()

except Exception as e:
    print("main", e)

sleep(2000)
mcu.reset()