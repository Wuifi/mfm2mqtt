#!/usr/bin/env python

## grabs data from the serial interface
import time
import serial
ser = serial.Serial(
 #port='/dev/ttyAMA0',
 port='/dev/ttyS0',
 baudrate = 19200,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

while True:
 raw=ser.readline()
 #print(raw)
 string=str(raw, 'UTF-8')
 string = string.replace('\r\n','') 
 print(string)
 
