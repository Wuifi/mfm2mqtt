#!/usr/bin/env python3
import time
import serial
import json
import paho.mqtt.client as mqtt
mqttc = mqtt.Client()
import paho.mqtt.publish as publish

## Configuration
MFM_SERIAL_PORT='/dev/ttyAMA0' #/dev/ttyS0'# os.environ.get('MFM_SERIAL_PORT')
nominal=50
SCRAPE_INTERVAL=0.1 # os.environ.get('SCRAPE_INTERVAL')

MQTT_TOPIC="mfm" # os.environ.get('MQTT_TOPIC')
MQTT_HOST="192.168.177.100" # os.environ.get('MQTT_TOPIC')
MQTT_PORT=1883 # os.environ.get('MQTT_TOPIC')
MQTT_CLIENT_ID="" # os.environ.get('MQTT_CLIENT_ID')
MQTT_KEEPALIVE=60 # os.environ.get('MQTT_KEEPALIVE')
MQTT_WILL=None # os.environ.get('MQTT_WILL')
MQTT_AUTH=None # os.environ.get('MQTT_AUTH')
MQTT_TLS=None # os.environ.get('MQTT_TLS')

###### Funktionen #####
def getmfmdata(MFM_SERIAL_PORT):
    #config serial interface
    ser = serial.Serial(
    port=MFM_SERIAL_PORT,
    baudrate = 19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
    )
    # check if serial connection is available
    try:
        raw=ser.readline()
        #mfm_1,hex
        #'49998\r\n'
        #print(raw)
        raw_str=str(raw, 'UTF-8')
        #print(raw_str)
        serial_ok=True
    except (ValueError, TypeError) as ex:
        #debug_str='"%s" cannot be converted to an float: %s' % (raw_str, ex)
        print(ex)
        serial_ok=False
        raw_str=""
    #if raw_str
    #"no valid frequency measurement"
    return raw_str, serial_ok

## convert data to json
def raw2json(raw_str,nominal):
    #lowerlimit=nominal*0.90
    #upperlimit=nominal*1.10
    min=None
    max=None
    mean=None
    try:
        #print('%s as an float is %d' % (str(raw_str), float(raw_str)))
        act_raw=float(raw_str)
        act_scaled=act_raw*0.001 # scale from mHz to Hz
        debug_str="OK"
        state_flag=1    
    except (ValueError, TypeError) as ex:
        act_scaled=0
        debug_str='"%s" cannot be converted to an float: %s' % (raw_str, ex)
        #print(debug_str)
        state_flag=-1
    json_string = {"MFM":{"FREQUENCY":{"actual":act_scaled,"min":min,"max":max},
                    "STATE":{"flag":state_flag,"debug":debug_str}}}
    #else:
    #    print('something else is wrong')
    #    act_scaled=0
    #    state_string='undefined fault'
    #print(act_scaled)
    #print(state_string)
    return json_string, state_flag 

## publish data 2 mqtt
def convert_to_mqtt_msg(topic,dict_input):
    json_object = json.dumps(dict_input, indent = 4)
    # Serializing json
    json_object = json.dumps(dict_input, indent = 4)
    #print(json_object)
    #print(type(json_object))
    msg = {'topic':topic, 'payload':json_object}
    #print(msg)
    #print(type(msg))
    return msg

def publish2mqtt(MQTT_msg):
    #print(MQTT_msg)   
    msgs = [MQTT_msg]
    # print(msgs)
    publish.multiple(
        msgs, hostname=MQTT_HOST,
        port=MQTT_PORT,
        client_id=MQTT_CLIENT_ID,
        keepalive=MQTT_KEEPALIVE,
        will=MQTT_WILL,
        auth=MQTT_AUTH,
        tls=MQTT_TLS,
        protocol=mqtt.MQTTv311,
        transport="tcp"
        )
    return 

while True:
    try:
        raw_str, serial_ok=getmfmdata(MFM_SERIAL_PORT)
        json_string, state_flag=raw2json(raw_str,nominal)
        print(json_string)
        MQTT_msg=convert_to_mqtt_msg(MQTT_TOPIC,json_string)
        publish2mqtt(MQTT_msg)
    except (ValueError, TypeError) as ex:
        #debug_str='"%s" cannot be converted to an float: %s' % (raw_str, ex)
        print(ex)
    time.sleep(SCRAPE_INTERVAL)


