# zlib adm
# Created at 2020-02-21 07:27:44.506933


import zlib_adm as adm
import mcu
from wireless import wifi
import sfw
from espressif.esp32net import esp32wifi as wifi_driver
import streams
import json


import testsuite as t



streams.serial()
sfw.watchdog(0,120000)

# mqtt_id = 'dev-4ncgqw30yiv7'
# password = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYtNG5jZ3F3MzB5aXY3IiwiZXhwIjoxNjAwNTIzNzI2LCJrZXkiOjF9.CQ9nhLHGpQi5tMLRRlCHUy3XPIns-Qr1xKtdJ5xBQP8'


# mqtt_id = 'dev-4pnefulyx2bn'
# pwd = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtNHBuZWZ1bHl4MmJuIiwidXNlciI6ImRldi00cG5lZnVseXgyYm4iLCJleHAiOjE5MTYyMzkwMjIsImtleSI6MX0.8Pi1y0s22ij1No-7oPysKGtpW0_ec7MMuZ3O5HeKqWw'

mqtt_id = 'dev-4py3x1xk2rkf'
pwd = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtNHB5M3gxeGsycmtmIiwidXNlciI6ImRldi00cHkzeDF4azJya2YiLCJrZXkiOjEsImV4cCI6MjUxNjIzOTAyMn0.a3H6XTmRRMAb0f1P6p4R9xyCZx4XiELbE18qJce07z0'

def rpc_custom_1(obj, arg):
    print("rpc_custom_1")
    print("arg:", arg)
    return {
        'value 1': random(0,100),
        'value 2': random(100,200)
        }

client = None 

def rpc_custom_2(obj, arg):
    print("rpc_custom_2")
    print("arg:", arg)
    return 'pre fota'


my_rpc = {
    'rpc1' : rpc_custom_1,
    'rpc2' : rpc_custom_2
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
    tags = [None,'asdad','asd/assssdd','1/2/3/asd']
    payload = {
        'topic': None,
        'value' : 0
    }
    for t in tags:
        payload['topic'] = t
        payload['value'] = random(0,100)
        client.publish(json.dumps(payload), t)
        
        print(t,':', payload)
    print("done")
    print(" ")


def pub_ufficio():
    print("---- publish ufficio ----")
    temp = random(19,23)
    pressure = random(50, 60)
    payload = {"temp": temp, "pressure": pressure}
    print(payload)
    client.publish(json.dumps(payload), 'ufficio')
    print("done")
    print(" ")


def upd_status():
    print("------ upd. status ------")
    key = 'my_dev_key'
    value = random(100,1000)
    print("value: ",value)
    client.update_status(key,value)
    print("done")
    print(" ")

def test():
    st = {'current':None, 'expected':None}
    
    p = 'arg'
    
    try:
        print("test")
        if 'expected' in st:
            for expected_key in st['expected']:
                print(expected_key)
        print("done if")
    except Exception as e:
        print("test", e)
    
    
def req_status():
    print("------ req. status ------")
    client.request_status()
    print("done")
    print(" ")



def t1():
    print("t1")
    return


def t2():
    print("t2")
    print("calling t1")
    a = t1()
    
    print(a)
    print("done")



t.add_command(pub_ufficio, 'ufficio')
t.add_command(pub_random,  'random')
t.add_command(upd_status, 'upd_st')
t.add_command(req_status, 'req_st')
t.add_command(test, 'test')
t.add_command(t2, 't2')
t.add_command(clear_st, 'clear')

try:
    
    wifi_driver.auto_init()
    for _ in range(5):
        try:
            print("connect wifi")
            wifi.link("Zerynth",wifi.WIFI_WPA2,"zerynthwifi")
            print("done")
            break
        except Exception as e:
            print("wifi connect err", e)
     
    client = adm.Thing(mqtt_id, rpc=my_rpc)
    
    # username is always == mqtt_id?
    client.set_password(pwd)
    
    
    client.connect()
    
    t.start()
    
    # i = 0
    # while True:
    #     sfw.kick()
    #     print("*************************")
        
    #     pub_random()
        
    #     pub_ufficio()
        
    #     upd_status()
        
    #     if i > 10:
    #         req_status()
    #         i=0
        
    #     i+=1
    #     sleep(2000)
        

except Exception as e:
    print("main", e)

sleep(2000)
mcu.reset()




