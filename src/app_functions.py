#!/usr/bin/python3

# import standard modules
import logging
import time
import json
# import 3rd party modules
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

# def mfmProtocolConverter(config,string):
#     #checks, what kind of information / protocol mfm is sending
#     protocol=config.getint('mfm', 'protocol')
#     print(string)
#     return



## convert data to json
def mfmstring2dict_P1(string):

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
    dict_output = {"MFM":{"FREQUENCY":{"actual":act_scaled},
                 "STATE":{"flag":state_flag,"debug":debug_str}}}

    return dict_output, state_flag 

def mfmstring2dict_P4(string):
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
