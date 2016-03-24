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

sys.path.append(os.getcwd() + '/../CAN')
import can_handler


class GPIO_Reader():
    def __init__(self):
        self.configureGPIO()
        self.low_input = False
        self.high_input = False
	self.period = 0.1

    def configureGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(19, GPIO.IN)
        GPIO.setup(26, GPIO.IN)

    def check_inputs(self):
        self.low_input = GPIO.input(26)
        self.high_input = GPIO.input(19)
        self.th_reader = threading.Timer(self.period, self.check_inputs)
	self.th_reader.start()

if __name__ == '__main__':

    reader = GPIO_Reader()
    reader.check_inputs()  # starts a thread

    can_h = can_handler.can_handler()
    can_h.configure('J1939')

    msg_ID = 0x1CFDCD00
    msg_stop = (0, 0, 0, 0, 0, 0, 0, 0)
    msg_low = (16, 0, 0, 0, 0, 0, 0, 0)

    msg_intermittence3s = (64, 0, 0xff, 0, 0, 0, 0, 0)
    msg_intermittence6s = (80, 0, 0xff, 0, 0, 0, 0, 0)

    '''actions'''
    while True:
        low = not reader.low_input
        high = not reader.high_input

        if (low is False and high is False):
            print "STOP"
            can_h.send_msg(msg_stop, msg_ID)
        elif (low is True and high is False):
            print "low speed"
            can_h.send_msg(msg_low, msg_ID)
        elif (low is False and high is True):
            print "high speed: not avaliable in katana"
        elif (low is True and high is True):
            print "intermittence"
            can_h.send_msg(msg_intermittence3s, msg_ID)
        else:
            print 'no function selected: stop'
            can_h.send_msg(msg_stop, msg_ID)

        sleep(0.500)
