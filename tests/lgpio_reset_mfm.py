#!/usr/bin/env python
#reset the mfm-board while LED is flashing every second
#https://gpiozero.readthedocs.io/
#from gpiozero import LED
import lgpio
from time import sleep
from mfm_functions import *

mfm_port = '/dev/ttyS0'
## settings for the HW-Interface to the LED-flashlight
LED = 18
#led = LED(18)
RESET = 25
#reset= LED(25) #reset PIN when the mfm-board is connected to the RPI GPIOs 

# open the gpio chip and set the LED pin as output
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, LED)
lgpio.gpio_claim_output(h, RESET)

try:
    print('mfm - reset script started')
    sleep(1)
    #led.on()
    #reset.on()
    lgpio.gpio_write(h, LED, 0)
    lgpio.gpio_write(h, RESET, 0)
    
    print('reset device on')
    sleep(1)
    #led.off()
    #reset.off()
    lgpio.gpio_write(h, LED, 1)
    lgpio.gpio_write(h, RESET, 1)
    print('reset device off')

    while True:
        #led.on()
        #print('LED on')

        raw,connection_ok=getrawdata(mfm_port)
        #print(raw)
        string=str(raw, 'UTF-8')
        string = string.replace('\r\n','') 

        list = string.split(";")
        valid=mfmOutputMonitor(list)
        print('valid: ',valid,' - Data - ',list)
        #sleep(1)
        #led.off()
        #print('LED off')
        #sleep(1)
        
except KeyboardInterrupt:
    lgpio.gpio_write(h, LED, 1)
    lgpio.gpio_write(h, RESET, 1)
    lgpio.gpiochip_close(h)
    print('Abbruch except KeyboardInterrupt')