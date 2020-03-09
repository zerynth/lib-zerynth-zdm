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


def rpc_list(obj, arg):
    return [k for k in obj.rpc]

def rpc_reset(obj, arg):
    return 'resetting device...'



class Thing():
    def __init__(self, mqtt_id, clicert=None, pkey=None, cacert=None, rpc=None, fota_callback=None):
        self.mqtt = ZADMMQTTClient(mqtt_id)
        self.mqtt_id = mqtt_id

        self.data_topic = '/'.join(['j','data',mqtt_id])
        self.up_topic = '/'.join(['j','up',mqtt_id])
        self.dn_topic = '/'.join(['j','dn',mqtt_id])

        self.current = {}
        self.expected = {} # ??

        self._fota_callback = fota_callback

        self.rpc = {
            'reset':rpc_reset
        }

        if type(rpc) == PDICT:
            self.rpc.update(rpc)
        elif rpc is not None:
            print("zlib_adm.Thing.__init__ rpc argument invalid")

    
    def set_password(self, pw):
        self.mqtt.set_username_pw(self.mqtt_id, pw)
        
    def connect(self):
        for _ in range(5):
            try:
                # print("zlib_adm.Thing.connect attempt")
                self.mqtt.connect(sock_keepalive=[1,10,5], aconnect_cb = self.subscribe)
                self.mqtt.loop()
                # print("zlib_adm.Thing.connect done")
                break
            except Exception as e:
                print("zlib_adm.Thing.connect", e)
                pass
        else:
            raise IOError
        self._config()



    def _config(self):
        # enable incoming messages callback and request status
        try:
            self.mqtt.on(mqtt.PUBLISH, self.handle_dn_msg)
            self.request_status()
            
            # TODO move on handle_delta_status
            self.send_manifest()
            self.send_vm_info()
            
        except Exception as e:
            print("zlib_adm.Thing._config", e)
            raise IOError




    def subscribe(self):
        try:
            # print("zlib_adm.Thing.subscribe attempt")
            self.mqtt.subscribe([[self.dn_topic,1]])
            print("zlib_adm.Thing.subscribe done")
        except Exception as e:
            print("zlib_adm.Thing.subscribe", e)
            raise IOError




    def handle_dn_msg(self, client, data):
        try:
            print("zlib_adm.Thing.handle_dn_msg received message")
            msg = data['message']
            print("raw", msg.payload)
            payload = json.loads(msg.payload)
            
            if 'key' in payload:
                if payload['key'][0] == '@':
                    # print("zlib_adm.Thing.handle_dn_msg received RPC @")
                    self.handle_rpc_request(payload['key'][1:], payload['value'])

                elif payload['key'][0] == '#':
                    # print("zlib_adm.Thing.handle_dn_msg received delta #")
                    self.handle_delta_request(payload['key'][1:], payload['value'])

                else:
                    print("zlib_adm.Thing.handle_dn_msg received custom")
                    # TODO
                    # pass payload['key'], payload['value'] to user callback ?
            else:
                print("zlib_adm.Thing.handle_dn_msg invalid message")
                # TODO
                # pass payload to user callback ?
        except Exception as e:
            print("zlib_adm.Thing.handle_dn_msg", e)


    def handle_rpc_request(self, rpc, arg):
        if rpc == 'fota':
            self.handle_fota_request(arg)
        elif rpc in self.rpc:
            # print("zlib_adm.Thing.handle_rpc_request user-defined request")
            try:
                res = self.rpc[rpc](self, arg)
            except Exception as e:
                print("zlib_adm.Thing.handle_rpc_request", e)
                res = 'exception'
            
            # TODO add skip reply to allow delayed response 
            self.reply_rpc(rpc, res)
        
            if rpc=='reset':
                mcu.reset()

        else:
            print("zlib_adm.Thing.handle_rpc_request invalid rpc request")
            # TODO
            # pass payload['key'], payload['value'] to user callback ?



    def handle_fota_request(self, arg):
        print("zlib_adm.Thing.handle_fota_request handling fota request")
        
        if not zfota.supported():
            print("zlib_adm.Thing.handle_fota_request fota not supported")
            response = {
                'fw_version' : arg['fw_version'],
                'result' : 'fail',
                'msg' : 'not supported by device'
            }
            self.reply_rpc('fota', response)
            return

        if self._fota_callback and (not self._fota_callback(arg['fw_version'])):
            print("zlib_adm.Thing.handle_fota_request fota aborted by callback")
            response = {
                "fw_version" : arg['fw_version'],
                "result" : "fail",
                "msg": 'aborted by callback'
            }
            self.reply_rpc('fota', response)
            return

        # fota supported and not aborted by callback
        # update _fota_status and request #fota_info
        
        value = {
            "fw_version" : arg['fw_version'],
            "progress" : 'waiting fota info'
        }
        self.update_status_key('_fota_status', value)
        
        
        value.pop("progress")
        self.request_delta('fota_info', value)

        return


    def handle_delta_request(self, delta_key, arg):
        # print("zlib_adm.Thing.handle_delta_request")
        if delta_key == 'status':
            self.handle_delta_status(arg)
            
        elif delta_key == 'fota_info':
            self.handle_delta_fota(arg)
            
        else:
            print("zlib_adm.Thing.handle_delta_request received user-defined delta")
            # TODO pass custom delta_key and arg to user callback?

    def handle_delta_status(self, arg):
        print("zlib_adm.Thing.handle_delta_status received status delta")
        
        if ('expected' in arg) and (arg['expected'] is not None):
            if '@fota' in arg['expected']:
                if ('current' in arg) and (arg['current'] is not None)  and ('_fota_status' in arg['current']):
                    # clear temp status key _fota_status
                    # close rpc (fail or success depending on valid), and finalize fota
                    # then reset becouse reasons (unstable fota record?)
                    
                    valid, msg = zfota.is_fota_valid()
                    
                    self.clear_status_key('_fota_status')
                    
                    value = {
                        "fw_version" : arg['expected']['@fota']['v']['fw_version'],
                        "result" : "success",
                        "msg": ""
                    }
                    
                    if valid:
                        zfota.finalize_fota()
                        value["result"] = "success"
                        
                    else:
                        value["result"] = "fail"
                        value["msg"] = msg
                    
                    self.reply_rpc('fota', value)
                    
                    sleep(1000)
                    mcu.reset()

                else:
                    value = arg['expected']['@fota']['v']
                    self.handle_fota_request(value)
                    return

            # handle other keys 
            for expected_key in arg['expected']:
                value = arg['expected'][expected_key]['v']

                if expected_key[0] == '@':
                    self.handle_rpc_request(expected_key[1:], value)
                else:
                    self.expected.update({expected_key: value})
        if ('current' in arg) and (arg['current'] is not None):
            for current_key in arg['current']:
                if current_key[0] == '_':
                    
                    print("skip current private key", current_key)
                else:
                    # print("current key:", current_key)
                    self.current.update({current_key: arg['current'][current_key]['v']})
            # TODO
            # move here check/update on __manifest and __vm_info keys

    def handle_delta_fota(self, arg):
        # print("zlib_adm.Thing.handle_delta_fota")

        possible, msg = zfota.is_fota_possible(arg['fw_metadata'])

        if not possible:
            print("zlib_adm.Thing.handle_delta_fota fota not possible:", msg)
            self.clear_status_key("_fota_status")
            
            response = {
                'fw_version' : arg['fw_version'],
                'result' : 'fail',
                'msg' : msg
            }
            self.reply_rpc('fota', response)
            return

        value = {
            "fw_version" : arg['fw_version'],
            "progress" : 'starting download'
        }
        self.update_status_key('_fota_status', value)
        
        
        # sleep(1000)
        self.fota_ongoing = True
        # self.mqtt.disconnect()
        # self.mqtt.close()
        # sleep(1000)
        status, message = zfota.handle_fota(arg)
        
    
        value["progress"] =  message
        self.update_status_key('_fota_status', value)
        
        sleep(1000)
        
        
        mcu.reset()





    def publish(self, data, tag=None):
        topic = self.data_topic
        if tag:
            topic += '/'+tag
        self.mqtt.publish(topic, data)


    def send_event(self, value):
        self.send_up_msg('','event',value)


    def update_status_key(self, key, value):
        # update key:value on adm and on self.current
        self.send_up_msg('',key,value)
        
        if key[0]!= '_':
            self.current[key]=value


    def clear_status_key(self, key):
        # remove status key from adm and self.current
        self.send_up_msg('',key,None)
        self.current.pop(key,None)


    def request_status(self):
        self.request_delta('status', {})
    
    def request_delta(self, key, value):
        self.send_up_msg('#',key, value)
    
    def reply_rpc(self, key, value):
        self.send_up_msg('@',key, value)
    
    
    def send_up_msg(self, prefix, key, value):
        msg = {
            'key' : prefix+key,
            'value' : value
        }
        self.mqtt.publish(self.up_topic, msg)
    
    
    def send_vm_info(self):
        vm_infos    = vm.info()
        vm_uid      = vm_infos[0]
        vm_target   = vm_infos[1]
        vm_ver      = vm_infos[2]
        value = {
            'vm_uid':vm_uid,
            'vm_target':vm_target,
            'vm_version':vm_ver
        }
        
        self.update_status_key("__vm_info", value)

    def send_manifest(self):
        value = [k for k in self.rpc]
        
        self.update_status_key("__manifest", value)
