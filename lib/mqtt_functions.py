#!/usr/bin/python3

# import standard modules
import logging
import time
import json
# import 3rd party modules
import paho.mqtt.client as mqtt
mqttc = mqtt.Client()
import paho.mqtt.publish as publish
import serial


default_log_level = logging.INFO
 

## publish data 2 mqtt
def convert_to_mqtt_msg(dict_input,config):
    try:
        # Serializing json   
        json_object = json.dumps(dict_input, indent = 4)  
        #print(json_object)
        #print(type(json_object))
        topic=config.get('mqtt', 'topic')
        msg = {'topic':topic, 'payload':json_object}
        #print(msg)
        #print(type(msg))
    except Exception  as e:
        logging.error("Error while converting data to json: ",str(e))
    return msg

def publish2mqtt(MQTT_msg,config):
    try:
        #print(MQTT_msg)   
        msgs = [MQTT_msg]
    # print(msgs)
        publish.multiple(
            msgs, hostname=config.get('mqtt', 'host'),
            port=config.getint('mqtt', 'port'),
            client_id=None,#config.get('mqtt', 'client_id'),
            keepalive=config.getint('mqtt', 'keepalive'),
            will=None,#config.get('mqtt', 'will'),
            auth=None,#config.get('mqtt', 'auth'),
            tls=None,#config.get('mqtt', 'tls'),
            protocol=mqtt.MQTTv311,#config.get('mqtt', 'protocol'),
            transport=config.get('mqtt', 'transport')
            )
    except Exception as e:
        logging.error("Failed to publish to MQTT <%s>: %s" % (config.get('mqtt', 'host'), str(e)))
    return 