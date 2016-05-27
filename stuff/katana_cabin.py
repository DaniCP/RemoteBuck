'''
@author: Daniel.Cano
Purpose:
This program translate digital inputs to CAN signals to KATANA project
'''

import sys
import os
import threading
import RPi.GPIO as GPIO
from time import sleep

sys.path.append(os.getcwd() + '..\CAN')
import can_handler


class GPIO_Reader():
    def __init__(self):
        self.configureGPIO()
        self.initUI()
        self.low_input = 0
        self.high_input = 0

    def configureGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN)
        GPIO.setup(24, GPIO.IN)
        GPIO.setup(25, GPIO.IN)

    def check_inputs(self, period):
        self.low_input = GPIO.input(25)
        self.high_input = GPIO.input(24)

        self.th_reader = threading.Timer(period, self.check_inputs)


if __name__ == '__main__':

    reader = GPIO_Reader()
    reader.check_inputs(0.1)  # starts a thread

    can_h = can_handler()
    can_h.configure('J1939')

    msg_ID = 0x1CFDCD00
    msg_stop = (0, 0, 0, 0, 0, 0, 0, 0)
    msg_low = (16, 0, 0, 0, 0, 0, 0, 0)

    msg_intermittence3s = (64, 0, 0xff, 0, 0, 0, 0, 0)
    msg_intermittence6s = (80, 0, 0xff, 0, 0, 0, 0, 0)

    '''actions'''
    while True:
        low = reader.low_input
        high = reader.high_input

        if (low==0 and high==0):
            print "STOP"
            can_h.send_msg(msg_stop, msg_ID)
        if (low==1 and high==0):
            print "low speed"
            can_h.send_msg(msg_low, msg_ID)
        elif (low==0 and high==1):
            print "high speed: not avaliable in katana"
        elif (low==1 and high==1):
            print "intermittence"
            can_h.send_msg(msg_intermittence3s, msg_ID)
        else:
            print 'no function selected: stop'
            can_h.send_msg(msg_stop, msg_ID)

        sleep(0.500)
