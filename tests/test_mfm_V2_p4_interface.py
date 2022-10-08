#!/usr/bin/env python3

## test of mfm V2 putput protocol 4 from the serial interface

# import standard modules
import logging
import time
import json

#from src.mfm_functions import *
from src.mfm_functions import MFMgetrawdata ,MFMmonitor
#import mfm_functions
#from mfm_functions import MFMgetrawdata ,MFMmonitor
#from src import mfm_functions

mfm_port = '/dev/ttyS0'

while True:
    raw,connection_ok=MFMgetrawdata(mfm_port)
    #print(connection_ok)
    #print(raw) # b'50028;+0276;0;0;0;0;0;0;0;0\r\n'
    #print(type(raw)) #<class 'bytes'>
    if (connection_ok == 1):
        string=str(raw, 'UTF-8')
        string = string.replace('\r\n','')
        list = string.split(";")
        valid = MFMmonitor(list)
        if (valid == 1):
            dict_meas, dict_mon, state_flag = MFMstring2dict_P4(list)
    
            print(dict_meas)
            print(dict_mon)
            print(state_flag)
    
    
    time.sleep(2)


