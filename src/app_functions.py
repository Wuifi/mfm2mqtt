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
    


# def mfmProtocolConverter(config,string):
#     #checks, what kind of information / protocol mfm is sending
#     protocol=config.getint('mfm', 'protocol')
#     print(string)
#     return






