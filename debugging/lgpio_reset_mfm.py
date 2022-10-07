#!/usr/bin/env python
#reset the mfm-board while LED is flashing every second
#https://gpiozero.readthedocs.io/
#from gpiozero import LED
import lgpio
from time import sleep
## settings for the HW-Interface to the LED-flashlight
LED = 18
#led = LED(18)
RESET = 25
#reset= LED(25) #reset PIN when the mfm-board is connected to the RPI GPIOs 

# open the gpio chip and set the LED pin as output
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, LED)
lgpio.gpio_claim_output(h, RESET)


import serial
ser = serial.Serial(
 port='/dev/ttyS0',
 baudrate = 19200,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)
try:
    print('mfm - reset script started')
    x=ser.readline()
    print(x)
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
        x=ser.readline()
        print(x)
        #sleep(1)
        #led.off()
        #print('LED off')
        #sleep(1)
        
except KeyboardInterrupt:
    lgpio.gpio_write(h, LED, 1)
    lgpio.gpio_write(h, RESET, 1)
    lgpio.gpiochip_close(h)
    print('Abbruch except KeyboardInterrupt')