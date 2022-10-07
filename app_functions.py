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

###### application specific functions #####
def getdata(config):
    raw=None
    connection_ok=False
    #config serial interface
    try:
        ser = serial.Serial(
        port=config.get('mfm', 'SERIAL_PORT'),
        baudrate = 19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
        )
    # read data from serial interface
        raw=ser.readline()
        #mfm_1,hex
        #'49998\r\n'
        logging.INFO("raw data received: %s", raw)
        connection_ok=True
    except Exception as e:
        logging.error("check connection! Error while getting data from device: %s", str(e))
    return raw,connection_ok
    
def convertraw2str(raw):
    try:
        string=str(raw, 'UTF-8')
        logging.INFO("raw data converted to string: %s", string)
        raw2str_ok=True
    except (ValueError, TypeError) as e:
        logging.error("Error while converting data to string: %s", str(e))
        raw2str_ok=False
        string=""
    return string, raw2str_ok

def freqmonitoring(config,act_scaled):
    #evaluates the measured frequency values and adds binary states
    #lowerlimit=config.getint('gridcode', 'lowerlimit1')*0.90
    #upperlimit=config.getint('gridcode', 'lowerlimit1')*1.10
    flagFLU1=0
    flagFLL1=0
    if ((act_scaled>=config.getint('gridcode', 'upperlimit1'))==True):
       flagFLU1=1 
    if ((act_scaled<=config.getint('gridcode', 'lowerlimit1'))==True):
       flagFLL1=1        
    flagdict={'flagFLU1':flagFLU1,'flagFLL1':flagFLL1}
    return flagdict

## convert data to json
def string2dict(string):
    min=None
    max=None
    mean=None
    try:
        act_raw=float(string)
        act_scaled=act_raw*0.001 # scale from mHz to Hz
        debug_str="OK"
        state_flag=1    
    except (ValueError, TypeError) as e:
        act_scaled=0
        debug_str='The value "%s" cannot be converted to float: %s' % (string, e)
        logging.error("Error while converting data to string: %s", str(e))
        state_flag=-1
    dict_output = {"MFM":{"FREQUENCY":{"actual":act_scaled,
                                        "min":min,
                                        "max":max,
                                        "mean":mean},
                 "STATE":{"flag":state_flag,"debug":debug_str}}}

    return dict_output, state_flag 
