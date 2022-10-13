#!/usr/bin/env python3
import logging
import serial

def MFMgetrawdata(mfm_port):
    raw=None
    connection_ok=0
    #config serial interface
    try:
        ser = serial.Serial(
        port=mfm_port,
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
        #logging.INFO("raw data received: %s", str(raw))
        
        connection_ok=1
    except Exception as e:
        connection_ok=0
        #logging.error("check connection! Error while getting data from device: %s", str(e))
    return raw,connection_ok



def MFMmonitor(list):
    #checks for any invalid data (e.g. during reset / auto detection)
    valid=0#'no measurement available'
     #['50028', '+0276', '0', '0', '0', '0', '0', '0', '0', '0\r\n']
    try:
        act_scaled = float(list[0])
        valid=1
    except:
        valid=0    
    return valid  
  
def MFMprotocol(list):
    try:
        if len(list) == 1: # protocol 1
            MFMprotocol = 1 
        if len(list) > 1: # protocol 2,3,4
            MFMprotocol = 4 # currently only version 4 is implemented
    except (ValueError, TypeError) as e:
        MFMprotocol=0
        debug_str='The protocol cannot be detected. InputList ="%s" : %s' % (str(list), str(e))
        logging.error('The protocol cannot be detected. InputList ="%s" : %s' % (str(list), str(e)))
    return MFMprotocol

    
        
def convertraw2str_P1(raw):
    try:
        string=str(raw, 'UTF-8')
        logging.INFO("raw data converted to string: %s", string)
        raw2str_ok=True
    except (ValueError, TypeError) as e:
        logging.error("Error while converting data to string: %s", str(e))
        raw2str_ok=False
        string=""
    return string, raw2str_ok
    
## convert data to json
def MFMstring2dict_P1(string):

    try:
        act_raw=float(string)
        act_scaled=act_raw*0.001 # scale from mHz to Hz
        state_flag=1    
    except (ValueError, TypeError) as e:
        act_scaled=0
        logging.error("Error while converting data to string: %s", str(e))
        state_flag=-1
    dict_meas = {"MFM":{"FREQUENCY":{"actual":act_scaled}}}
    dict_mon = {"MFM":{"STATE":{"flag":state_flag}}}
    return dict_meas, dict_mon, state_flag 

def MFMlist2dict_P4(list):
    ## convert data to json
    act_scaled = None
    p_raw = None
    freqMon = [None, None, None, None, None, None, None, None]
    debug_str="FLT"
    state_flag=-1 
    try:
        act_scaled = float(list[0])*0.001 # scale from mHz to Hz #50.025 Hz
        if (act_scaled>=45.0):
            debug_str="OK"
            state_flag=1 
        
        if len(list) > 1: # protocol 4
            p_raw = float(list[1]) #76.0 / -76.0

            freqMon = list[2:]
            freqMon = [int(i) for i in freqMon]
          
    except (ValueError, TypeError) as e:
        act_scaled=0
        debug_str='The value "%s" cannot be converted to float: %s' % (str(list), e)
        logging.error("Error while converting data to string: %s", str(e))
        state_flag=-1
    dict_meas = {"MFM":{"FREQUENCY":{"actual":act_scaled,"p_raw":p_raw,
                                        "freqMon":freqMon}}}
    dict_mon = {"MFM":{"STATE":{"flag":state_flag}}}
    return dict_meas, dict_mon, state_flag 
    
