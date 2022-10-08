#!/usr/bin/env python3

## grabs data from the serial interface

# import standard modules
import logging
import time
import json

#from mfm_functions import *
#import lib.mfm_functions
from lib import mfm_functions

mfm_port = '/dev/ttyS0'

while True:
    raw,connection_ok=getrawdata(mfm_port)
    #print(connection_ok)
    #print(raw) # b'50028;+0276;0;0;0;0;0;0;0;0\r\n'
    #print(type(raw)) #<class 'bytes'>
    if (connection_ok == 1):
        string=str(raw, 'UTF-8')
        string = string.replace('\r\n','')
        list = string.split(";")
        valid = mfmOutputMonitor(list)
        if (valid == 1):
            dict_meas, dict_mon, state_flag = mfmstring2dict_P4(list)
    
            print(dict_meas)
            print(dict_mon)
            print(state_flag)
    
    
    time.sleep(2)


