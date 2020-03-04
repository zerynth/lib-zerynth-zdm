# zlib adm
# Created at 2020-02-21 07:27:44.506933


import zlib_adm as adm
import mcu

mqtt_id = 'dev-4ncgqw30yiv7'

password = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYtNG5jZ3F3MzB5aXY3IiwiZXhwIjoxNjAwNTIzNzI2LCJrZXkiOjF9.CQ9nhLHGpQi5tMLRRlCHUy3XPIns-Qr1xKtdJ5xBQP8'


def rpc_custom_1(arg):
    print("rpc_custom_1")
    print("arg:", arg)
    

def rpc_custom_2(arg):
    print("rpc_custom_2")
    print("arg:", arg)

my_rpc = {
    'rpc1' : rpc_custom_1,
    'rpc2' : rpc_custom_2
}

try:
    client = adm.Thing(mqtt_id, rpc=my_rpc)

    # client username must be always equal to client id - username is set by this function
    client.set_password(password)
    
    client.connect()


except Exception as e:
    print("main", e)

sleep(2000)
mcu.reset()