#!/usr/bin/env python
import ctypes as ct
import sys
import struct
import logging
import inspect
from bitstring import BitArray, Bits

from time import sleep
import time
import threading
import canlib


class periodic_frame_sender():
    def __init__(self, can_h=None, period=None, msgId=None, msg=None):
        self.can_h = can_h
        self.period = period
        self.msgId = msgId
        self.msg = msg

    def configure(self, can_h, period, msgId, msg):
        self.can_h = can_h
        self.period = period
        self.msgId = msgId
        self.msg = msg

    def start_frame(self):
        can_h.send_msg(self.msg, msgId)
        self.th_periodic = threading.Timer(self.period, self.start_frame)
        self.th_periodic.start()

    def stop_frame(self):
        self.th_periodic.cancel()


class can_handler():
    def __init__(self):
        self.canLib = canlib.canlib()

    def configure(self):
        '''Function to open channel, set bitrate, and enable bus'''

        if self.canLib.getNumberOfChannels() < 3:
            print 'CAN driver not found'
        else:
            try:
                self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_ACCEPT_VIRTUAL)
                self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                self.ch1.setBusParams(canlib.canBITRATE_125K)
                self.ch1.busOn()
            except (self.canlib.canError) as ex:
                print(ex)

    def send_msg(self, msg, msgId, flg=False):
        msg_writen = "".join("0x%02x " %  b for b in msg)
        print "write: ", msg_writen
        try:
            self.ch1.write(msgId, msg, flg)
#             sleep(0.5)
        except (self.canLib.canNoMsg) as ex:
            None
        except (self.canLib.canError) as ex:
            print(ex)

    def read_msg_and_print(self):
        msgId, msg, dlc, flg, time = self.ch1.read(timeout=2000)
        msg_received = "".join("0x%02x " % b for b in msg)
        print "read: ", msg_received
#         print("read: 0x%03x  %9d  0x%02x  %d  %s" % (msgId, time, flg, dlc, msg))

    def start_heartbeat(self):
        heartbeat = [0x7F]
        self.send_msg(heartbeat, 0x764)
        self.th_HB = threading.Timer(0.5, self.start_heartbeat)
        self.th_HB.start()

    def stop_heartbeat(self):
        self.th_HB.cancel()

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
    msg_set_heartbeat = (0x23, 0x16, 0x10, 0x01, 0xdc, 0x05, 0x64, 0x00)

    grader_ID = 0x1CFDE8FC
    msg_grader = (0xD4, 0x00, 0x12, 0x00, 0x00, 0x12, 0x02, 0x01)

    write_buffer = (msg_clear_error, msg_mode_speed, msg_set_speed, msg_break_on, msg_set_heartbeat)

    """bus interaction"""
#     can_h.start_heartbeat()
    heartbeat = periodic_frame_sender(can_h=can_h, period=0.5, msgId=0x764, msg=[0x7F])
    heartbeat.start_frame()
    for msg in write_buffer:
        can_h.send_msg(msg, msgId)
        can_h.read_msg_and_print()

    sleep(20)
#     can_h.stop_heartbeat()
    heartbeat.stop_frame()
    print '**** END PROGRAM ****'
