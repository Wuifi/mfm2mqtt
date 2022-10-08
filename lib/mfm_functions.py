#!/usr/bin/env python3
import logging
import serial

def getrawdata(mfm_port):
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
 
def mfmOutputMonitor(list):
    #checks for any invalid data (e.g. during reset / auto detection)
    valid=0#'no measurement available'
     #['50028', '+0276', '0', '0', '0', '0', '0', '0', '0', '0\r\n']
    try:
        act_scaled = float(list[0])
        valid=1
    except:
        valid=0    
    return valid    

## convert data to json
def mfmstring2dict_P4(list):
    act_scaled = None
    p_raw = None
    freqMon = [None, None, None, None, None, None, None, None]
    debug_str="FLT"
    state_flag=-1 
    try:
        act_scaled = float(list[0])*0.001 # scale from mHz to Hz #50.025 Hz

        p_raw = float(list[1]) #76.0 / -76.0

        freqMon = list[2:]
        freqMon = [int(i) for i in freqMon]

        if (act_scaled>=45.0):
            debug_str="OK"
            state_flag=1 
           
    except (ValueError, TypeError) as e:
        act_scaled=0
        debug_str='The value "%s" cannot be converted to float: %s' % (str(list), e)
        logging.error("Error while converting data to string: %s", str(e))
        state_flag=-1
    dict_meas = {"MFM":{"FREQUENCY":{"actual":act_scaled,"p_raw":p_raw,
                                        "freqMon":freqMon}}}
    dict_mon = {"MFM":{"STATE":{"flag":state_flag}}}
    return dict_meas, dict_mon, state_flag 
    
