from mqtt import mqtt
import json

ENDPOINT = "rmq.zerinth.com"
PORT = 1883


class ZADMMQTTClient(mqtt.Client):
    def __init__(self, mqtt_id, endpoint=ENDPOINT, ssl_ctx=None, clean_session=True):
        mqtt.Client.__init__(self, mqtt_id, clean_session=clean_session)
        self.endpoint = endpoint
        self.ssl_ctx = ssl_ctx
    
    def connect(self, port=PORT, sock_keepalive=None, aconnect_cb=None, breconnect_cb=None):
        is self.ssl_ctx is not None:
            mqtt.Client.connect(self, self.endpoint, 60, port=port, ssl_ctx=self.ssl_ctx, sock_keepalive=sock_keepalive, aconnect_cb=aconnect_cb, breconnect_cb=breconnect_cb)
        else:
            mqtt.Client.connect(self, self.endpoint, 60, port=port, sock_keepalive=sock_keepalive, aconnect_cb=aconnect_cb, breconnect_cb=breconnect_cb)
    
    def publish(self, topic, payload):
        if type(payload) == PDICT:
            payload = json.dumps(payload)
        mqtt.Client.publish(self, topic, payload)
    
    
class Thing():
    def __init__(self, mqtt_id, clicert=None, pkey=None, cacert=None, rpc=None):
        
        self.mqtt = ZADMMQTTClient(mqtt_id)
        self.mqtt_id = mqtt_id
    
        self.data_topic = '/'.join(['j','data',mqtt_id])
        self.up_topic = '/'.join(['j','up',mqtt_id])
        self.dn_topic = '/'.join(['j','dn',mqtt_id])
        
        self.rpc = {}
        
        if type(rpc) == PDICT:
            self.rpc.update(rpc)


    def connect(self):
        for _ in range(5):
            try:
                self.mqtt.connect(sock_keepalive=[1,10,5], aconnect_cb = self.subscribe)
                self.mqtt.loop()
                break
            except Exception as e:
                print("zlib_adm.Thing.connect", e)
                pass
        else:
            raise IOError
        
        self._config()
    
    def _config(self):
        try:
            self.mqtt.on(mqtt.PUBLISH, self.handle_dn_msg)
        except Exception as e:
            print("zlib_adm.Thing._config", e)
            raise IOError
            
    def subscribe(self):
        try:
            self.mqtt.subscribe([[self.dn_topic,1]])
        except Exception as e:
            print("zlib_adm.Thing.subscribe", e)
            raise IOError
        
    def handle_dn_msg(self, client, data):

        try:
            print("handle_dn_msg")
            for k in data:
                print(k)
            print("-------")
        except Exception as e:
            print("zlib_adm.Thing.handle_dn_msg", e)
          
        try:
            msg = data['message']
            payload = json.loads(msg.payload)

        except Exception as e:
            print("zlib_adm.Thing.handle_dn_msg", e)
          
    
    def set_password(self, pw):
        self.mqtt.set_username_pw(self.mqtt_id, pw)
    