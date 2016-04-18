#!/usr/bin/env python
import ctypes as ct
import sys
import struct
import logging
import inspect
from bitstring import BitArray, Bits
from time import sleep

from threading import Thread

import canlib


class can_handler():
    def __init__(self):
        self.canLib = canlib.canlib()

    def configure(self):
        if self.canLib.getNumberOfChannels() < 3:
            print 'CAN driver not found'
        else:
            try:
                self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_ACCEPT_VIRTUAL)
                self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                self.ch1.setBusParams(canlib.canBITRATE_250K)
                self.ch1.busOn()
            except (self.canlib.canError) as ex:
                print(ex)
    
    def send_msg(self, msg, msgId, flg=False):
        try:
#             dlc, flg, time = 8, False, 8
#             msgId = 0x601
#             msg = (0x2f, 0x04, 0x21, 0x00, 0x01, 0x00, 0x00, 0x00)
#             print("%9d  %9d  0x%02x  %d  %s" % (msgId, time, flg, dlc, msg))

            self.ch1.write(msgId, msg, flg)
            sleep(0.5)

        except (self.canLib.canNoMsg) as ex:
            None
        except (self.canLib.canError) as ex:
            print(ex)

if __name__ == '__main__':
    can_h = can_handler()
    can_h.configure()
    msgId = 0x601
    OFF = 0x00
    ON = 0x01

    msg_clear_error = (0x2f, 0x02, 0x21, 0x01, 0x01, 0x00, 0x00, 0x00)
    msg_mode_speed = (0x2f, 0x03, 0x21, 0x00, 0x02, 0x00, 0x00, 0x00)
    msg_set_speed = (0x23, 0x01, 0x22, 0x00, 0xfa, 0x00, 0x00, 0x00)
    msg_break_on = (0x2f, 0x04, 0x21, 0x00, ON, 0x00, 0x00, 0x00)

    write_buffer = (msg_clear_error, msg_mode_speed, msg_set_speed, msg_break_on)

    for msg in write_buffer:
        can_h.send_msg(msg, msgId)

