import json

from mqtt import mqtt


# jwt_token = "!!! COPY THE JWT TOKEN HERE !!!"

class Device():
    """
================
The Device class
================
    """

    def __init__(self, uid, token, endpoint='rmq.zerinth.com', port=1883, rpc=None, log=False,
                 fota_callback=None, low_res=False):
        self.publish_topic = '.'.join(['j', 'data', uid, 'prova'])
        self.down_topic = '/'.join(['j', 'dn', uid])
        self.up_topic = '/'.join(['j', 'up', uid])

        # mqtt client_id must be equal to the device id
        client = mqtt.Client(uid, clean_session=True)
        client.set_username_pw(uid, token)

        for retry in range(10):
            try:
                client.connect(endpoint, 60, port)
                break
            except Exception as e:
                print("connecting...", e)
        print("connected.")

        # subscribe to channels
        client.subscribe([[self.down_topic, 1]])

        # client.on(mqtt.PUBLISH, print_sample, condition=is_sample)

        client.loop()

    def send_data(self, payload):
        """
    .. method:: send_data(payload)

        Send a data containing the payload :samp:`payload` to the ADM. Payload is given as a dictionary and then serialized to JSON.

        """
        jpayload = json.dumps(payload)
        self.client.publish(self.publish_topic, jpayload, qos=1)
