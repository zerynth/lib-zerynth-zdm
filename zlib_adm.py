from mqtt import mqtt
import json
import mcu
import vm

import zlib_adm_fota as zfota

ENDPOINT = "rmq.adm.zerinth.com"
PORT = 1883


class ZADMMQTTClient(mqtt.Client):
    def __init__(self, mqtt_id, endpoint=ENDPOINT, ssl_ctx=None, clean_session=True):
        mqtt.Client.__init__(self, mqtt_id, clean_session=clean_session)
        self.endpoint = endpoint
        self.ssl_ctx = ssl_ctx
    
    def connect(self, port=PORT, sock_keepalive=None, aconnect_cb=None, breconnect_cb=None):
        mqtt.Client.connect(self, self.endpoint, 60, port=port, sock_keepalive=sock_keepalive, aconnect_cb=aconnect_cb, breconnect_cb=breconnect_cb)

        # is self.ssl_ctx is not None:
        #     mqtt.Client.connect(self, self.endpoint, 60, port=port, ssl_ctx=self.ssl_ctx, sock_keepalive=sock_keepalive, aconnect_cb=aconnect_cb, breconnect_cb=breconnect_cb)
        # else:
        #     mqtt.Client.connect(self, self.endpoint, 60, port=port, sock_keepalive=sock_keepalive, aconnect_cb=aconnect_cb, breconnect_cb=breconnect_cb)
    
    def publish(self, topic, payload):
        if type(payload) == PDICT:
            payload = json.dumps(payload)
        
        mqtt.Client.publish(self, topic, payload)


def rpc_list(obj, *args):
    return [k for k in obj.rpc]

def rpc_reset(obj, *args):
    print("rpc reset device")
    
    
class Thing():
    def __init__(self, mqtt_id, clicert=None, pkey=None, cacert=None, rpc=None, fota_callback=None):
        
        self.mqtt = ZADMMQTTClient(mqtt_id)
        self.mqtt_id = mqtt_id
    
        self.data_topic = '/'.join(['j','data',mqtt_id])
        self.up_topic = '/'.join(['j','up',mqtt_id])
        self.dn_topic = '/'.join(['j','dn',mqtt_id])
        
        self.rpc = {
            'reset':rpc_reset
        }
        
        self.expected = {}
        self.current = {}
        
        self.fota_callback = fota_callback
        
        if type(rpc) == PDICT:
            self.rpc.update(rpc)
        elif rpc is not None:
            print("zlib_adm.Thing.__init__ rpc argument invalid")
        
        
    def connect(self):
        for _ in range(5):
            try:
                print("zlib_adm.Thing.connect attempt")
                self.mqtt.connect(sock_keepalive=[1,10,5], aconnect_cb = self.subscribe)
                self.mqtt.loop()
                print("zlib_adm.Thing.connect done")
                break
            except Exception as e:
                print("zlib_adm.Thing.connect", e)
                pass
        else:
            raise IOError
        self._config()


    
    def _config(self):
        # enable incoming messages callback and publish fota_record
        
        try:
            self.mqtt.on(mqtt.PUBLISH, self.handle_dn_msg)

            self.send_manifest()
            self.send_vm_info()
            self.request_status()
            
        except Exception as e:
            print("zlib_adm.Thing._config", e)
            raise IOError
    
    
    def send_vm_info(self):
        asd = vm.info()
        vm_uid = asd[0]
        vm_target = asd[1]
        vm_ver = asd[2]
      
        payload = {
            'key' : '__vm_info',
            'value': {
                'vm_uid':vm_uid,
                'vm_target':vm_target,
                'vm_version':vm_ver
            }
        }
        
        self.mqtt.publish(self.up_topic, json.dumps(payload))
    
    def send_manifest(self):
        payload = {
            'key' : '__manifest',
            'value': [k for k in self.rpc]
        }
        self.mqtt.publish(self.up_topic, json.dumps(payload))
    
        

    def subscribe(self):
        try:
            print("zlib_adm.Thing.subscribe attempt")
            self.mqtt.subscribe([[self.dn_topic,1]])
            print("zlib_adm.Thing.subscribe done")
        except Exception as e:
            print("zlib_adm.Thing.subscribe", e)
            raise IOError
        
        
    
    def handle_delta_request(self, delta_key, arg):
        print("zlib_adm.Thing.handle_delta_request")
        print("delta_key", delta_key)
        print("arg", arg)
        
        if delta_key == 'status':
            print("zlib_adm.Thing.handle_delta_request received status delta")
        
            if ('expected' in arg) and (arg['expected'] is not None):
                
                if '@fota' in arg['expected']:
                    if ('current' in arg) and (arg['current'] is not None) and ('fota_status' in arg['current']):
                        valid, msg = zfota.is_fota_valid(arg['current']['fota_status'])
                        
                        if valid:
                            
                            # clear fota_status status
                            payload = {
                                'key' : 'fota_status',
                                'value': None
                            }
                            self.mqtt.publish(self.up_topic, json.dumps(payload))
                            
                            # TODO where is fw_version in @fota or fota_status? v? value?...
                            # close fota success
                            answer = {
                                'key' : '@fota',
                                'value' : {
                                    "fw_version" : arg['expected']['@fota'],
                                    "result" : "success",
                                    "msg": ""
                                }
                            }
                            print("zlib_adm.Thing.handle_rpc_request answer", answer)
                            self.mqtt.publish(self.up_topic, json.dumps(answer))
                            # mcu reset to validate fota record
                            sleep(1000)
                            mcu.reset()
                        else:
                            
                            # clear fota_status status
                            payload = {
                                'key' : 'fota_status',
                                'value': None
                            }
                            self.mqtt.publish(self.up_topic, json.dumps(payload))
                            
                            # TODO where is fw_version in @fota or fota_status? v? value?...
                            # TODO msg last_working_slot vs current_slot: "tried and failed" or "somwthing gone wrong during download.."
                            answer = {
                                'key' : '@fota',
                                'value' : {
                                    "fw_version" : arg['expected']['@fota'],
                                    "result" : "fail",
                                    "msg": ""
                                }
                            }
                            print("zlib_adm.Thing.handle_rpc_request answer", answer)
                            self.mqtt.publish(self.up_topic, json.dumps(answer))
                            sleep(1000)
                            
                            # TODO reset only if fota_record is not "stable"
                            mcu.reset()
                            
                    else:
                        pass
                        
                
                for expected_key in arg['expected']:
                    value = arg['expected'][expected_key]

                    
                    if expected_key[0] == '@':
                        self.handle_rpc_request(expected_key[1:], value)
        #                 # if expected_key not in arg['current']:
        #                 #     self.handle_rpc_request(expected_key[1:], value)
        #                 # else:
        #                 #     print("zlib_adm.Thing.handle_delta_request ignoring rpc, already answered")
                    else:
                        self.expected.update({delta_key: arg})
        
        elif delta_key == 'fota_info':
            print("zlib_adm.Thing.handle_delta_request received fota_info delta")
            print("arg:", arg)
            
            possible, msg = zfota.is_fota_possible(arg['fw_metadata'])
            
            if not possible:
                print("fota not possible notify fota_status progress")
            
                payload = {
                    'key' : 'fota_status',
                    'value': None
                }
                self.mqtt.publish(self.up_topic, json.dumps(payload))
                
                
                print("close @fota")
                answer = {
                    'key' : '@fota',
                    'value' : {
                        "fw_version" : arg['fw_version'],
                        "result" : "fail",
                        "msg": msg
                    }
                }
                
                print("zlib_adm.Thing.handle_rpc_request answer", answer)
                self.mqtt.publish(self.up_topic, json.dumps(answer))
                print("zlib_adm.Thing.handle_rpc_request done")
                return
            
            
            # fota is possible / metadata are valid
            
            payload = {
                'key' : 'fota_status',
                'value': {
                    "fw_version" : arg['fw_version'],
                    'bc_slot' : arg['fw_metadata']['bc_slot'],
                    # 'vm_slot' : arg['fw_metadata']['vm_slot'],
                    'vm_uid' : arg['fw_metadata']['vm_uid'],
                    "progress" : 'download started'
                }
            }
            
            self.mqtt.publish(self.up_topic, json.dumps(payload))
            
            
            sleep(1000)
            self.fota_ongoing = True
            
            self.mqtt.disconnect()
            self.mqtt.close()
            
            sleep(1000)
            
            status, message = zfota.handle_fota(arg)
            
            # obj.upd_job(jobid, status, message)
            mcu.reset()

        else:
            print("zlib_adm.Thing.handle_delta_request received user-defined delta")





    def handle_rpc_request(self, rpc, arg):
        
        if rpc == 'fota':
            print("zlib_adm.Thing.handle_rpc_request received fota request")
            
            if not zfota.supported():
                
                print("fota not supported")
                
                answer = {
                    'key' : '@fota',
                    'value' : {
                        "fw_version" : arg['fw_version'],
                        "result" : "fail",
                        "msg": 'fota not supported by device'
                    }
                }
                
                print("zlib_adm.Thing.handle_rpc_request answer", answer)
                self.mqtt.publish(self.up_topic, json.dumps(answer))
                print("zlib_adm.Thing.handle_rpc_request done")
                
                return
            
            if self.fota_callback and (not self.fota_callback(arg['fw_version'])):
                print("fota aborted by callback")
                
                answer = {
                    'key' : '@fota',
                    'value' : {
                        "fw_version" : arg['fw_version'],
                        "result" : "fail",
                        "msg": 'aborted by callback'
                    }
                }
                
                print("zlib_adm.Thing.handle_rpc_request answer", answer)
                self.mqtt.publish(self.up_topic, json.dumps(answer))
                print("zlib_adm.Thing.handle_rpc_request done")
                    
                return
            
            
            # fota supported and not aborted by callback
            print("fota can proceed notify fota_status progress")
            payload = {
                'key' : 'fota_status',
                'value': {
                    "fw_version" : arg['fw_version'],
                    "progress" : 'waiting fota details'
                }
            }
            self.mqtt.publish(self.up_topic, json.dumps(payload))
            
            
            print("asking fota info")
            payload = {
                'key' : '#fota_info',
                'value': {
                    "fw_version" : arg['fw_version']
                }
            }
            self.mqtt.publish(self.up_topic, json.dumps(payload))
            
            return
        
        
        
        elif rpc in self.rpc:
            print("zlib_adm.Thing.handle_rpc_request user-defined request")
            try:
                res = self.rpc[rpc](self, arg)
            
            except Exception as e:
                print("zlib_adm.Thing.handle_rpc_request", e)
            
                res = 'ZADM error'
            
            answer = {
                'key' : '@'+rpc,
                'value' : res
            }
            
            print("zlib_adm.Thing.handle_rpc_request", answer)
            self.mqtt.publish(self.up_topic, json.dumps(answer))
            
            if rpc=='reset':
                mcu.reset()
            
        else:
            print("zlib_adm.Thing.handle_rpc_request invalid rpc request")
    
    
    
    
    def handle_dn_msg(self, client, data):
        print("zlib_adm.Thing.handle_dn_msg")
        
        # try:
        #     for k in data:
        #         print(k)
        #     print("-------")
        # except Exception as e:
        #     print("zlib_adm.Thing.handle_dn_msg", e)
        
        
        try:
            print("* * * ")
            msg = data['message']
            print("raw", msg.payload)
            payload = json.loads(msg.payload)
            print(" ")
            print("dict", payload)
            
            if 'key' in payload:
                if payload['key'][0] == '@':
                    print("received RPC @")
                    # self.handle_rpc(payload)
                    self.handle_rpc_request(payload['key'][1:], payload['value'])
                    
                
                elif payload['key'][0] == '#':
                    print("received internal status #")
                    
                    # self.handle_delta(payload)
                    
                    self.handle_delta_request(payload['key'][1:], payload['value'])
                    
                else:
                    print("received custom key")
            
            else:
                print("received invalid message")
            
        except Exception as e:
            print("zlib_adm.Thing.handle_dn_msg", e)
        print("* * * ")

    
    def set_password(self, pw):
        self.mqtt.set_username_pw(self.mqtt_id, pw)
    
    
    def publish(self, data, tag=None):
        topic = self.data_topic
        if tag:
            topic += '/'+tag
            
        self.mqtt.publish(topic, data)
        print("publish done")
    
    def update_status(self, key, value):
        payload = {
            'key' : key,
            'value' : value
        }
        self.mqtt.publish(self.up_topic, json.dumps(payload))
        print("update_status done")
        
    def send_event(self, value):
        # lato device è come update_status (me lo ritrovo tra le chiavi quando chiedo #status)
        # lato adm, tutti gli event vengono salvati anche da un'altra parte
        payload = {
            'key' : 'event',
            'value' : value
        }
        self.mqtt.publish(self.up_topic, json.dumps(payload))
        print("send_event done")
    
    
    def clear_status_key(self, key):
        payload = {
            'key' : key,
            'value': None
        }
        self.mqtt.publish(self.up_topic, json.dumps(payload))
        print("clear status key", key,"done")
        
    def request_status(self):
        payload = {
            'key' : '#status',
            'value':{}
        }
        self.mqtt.publish(self.up_topic, json.dumps(payload))
        print("request_status done")