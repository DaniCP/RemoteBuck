#!/usr/bin/env python
import ctypes as ct
import sys
import struct
import inspect
from bitstring import BitArray, Bits
import Queue
import logging

from time import sleep
import time
import threading
import canlib


class periodic_frame_sender():
    def __init__(self, can_h=None, period=None, msgId=None, msg=None):
        self.can_h = can_h
        self.period = period # seconds
        self.msgId = msgId
        self.msg = msg

    def configure(self, can_h, period, msgId, msg):
        self.can_h = can_h
        self.period = period
        self.msgId = msgId
        self.msg = msg

    def start_frame(self):
        self.can_h.send_msg(self.msg, self.msgId)
        self.th_periodic = threading.Timer(self.period, self.start_frame)
        self.th_periodic.start()

    def stop_frame(self):
        self.th_periodic.cancel()


class periodic_reader():
    def __init__(self, can_h=None, period=0.1, logger=None):
        self.can_h = can_h
        self.period = period  # seconds
        self.th_periodic = None
        self.read_msg_list = []
        self.rx_queue = Queue.Queue()
        self.logger = logger

    def configure(self, period=None):
        self.can_h = can_h
        self.period = period

    def read_buffer(self):
        try:
            while True:
                msgId, msg, dlc, flg, time = self.can_h.ch1.read(timeout=1)
                msg_received = "".join("0x%02x " % b for b in msg)
                self.logger.info('%s %s %s %s', time, dlc, msgId, msg_received)
                self.rx_queue.put((time, msgId, msg_received))
        except:
#             print "msg_count:\n", self.rx_queue.get()
            self.th_periodic = threading.Timer(self.period, self.read_buffer)
            self.read_msg_list = []
            self.th_periodic.start()

    def start_to_read(self):
        self.read_buffer()

    def stop_reader(self):
        self.th_periodic.cancel()


class can_handler():
    def __init__(self):
        self.canLib = canlib.canlib()
        self.reader_period = 0.01 #seconds
        self.old_read_msg = ''
        self.read_msg_list = []

    def configure(self, bus_type='J1939'):
        '''Function to open channel, set bitrate, and enable bus
            input:    type: J1939 or CANOpen'''

        if self.canLib.getNumberOfChannels() < 1:
            print 'CAN driver not found, number of channels: ', self.canLib.getNumberOfChannels()
        else:
            try:
                if bus_type == 'J1939':
                    self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_REQUIRE_EXTENDED + canlib.canOPEN_ACCEPT_VIRTUAL)
                    self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                    self.ch1.setBusParams(canlib.canBITRATE_250K)
                elif bus_type == 'CANOpen':
                    self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_ACCEPT_VIRTUAL)
                    self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                    self.ch1.setBusParams(canlib.canBITRATE_125K)
                else:   # default J1939
                    self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_REQUIRE_EXTENDED + canlib.canOPEN_ACCEPT_VIRTUAL)
                    self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                    self.ch1.setBusParams(canlib.canBITRATE_250K)

                self.ch1.busOn()
            except (self.canlib.canError) as ex:
                print(ex)

    def send_msg(self, msg, msgId, flg=False):
        msg_writen = "".join("0x%02x " %  b for b in msg)
#         flg = canlib.canMSG_EXT
        flg = 0
#         print "write: ", msg_writen
        try:
            self.ch1.write(msgId, msg, flg)
#             sleep(0.100)
            sleep(0.001)
        except:
            print "*************************    EXCEPTION WHILE WRITE    **********************"
            sleep(0.3)
            self.ch1.busOff()
            self.ch1.close()
            self.configure()
            self.ch1.write(msgId, msg, flg)
#         except (self.canLib.canNoMsg) as ex:
#             None
#         except (self.canLib.canError) as ex:
#             print(ex)

    def read_msg_and_print(self):
        msgId, msg, dlc, flg, time = self.ch1.read(timeout=2000)
        msg_received = "".join("0x%02x " % b for b in msg)
        print "read: ", msg_received
#         print("read: 0x%03x  %9d  0x%02x  %d  %s" % (msgId, time, flg, dlc, msg))

    def read_msg(self, timeout=2000):
        try:
            msgId, msg, dlc, flg, time = self.ch1.read(timeout)
#         msg_received = "".join("0x%02x " % b for b in msg)
#         print 'read: ', msgId, msg, time
            return msg, msgId, time
        except:
            print '*****    exception while READ    *****'
            return -1, -1, -1

    '''trying to read periodic mesages'''
    def reader_start(self):
        msgId, msg, dlc, flg, time = self.ch1.read(timeout=200)
        msg_received = "".join("0x%02x " % b for b in msg)
        if msg_received != self.old_read_msg:
            print 'read: ', msg_received, 'time: ', time
        self.th_reader = threading.Timer(self.reader_period, self.reader_start)
        self.th_reader.start()
        self.old_read_msg = msg_received

    def reset_reader_counter(self):
        self.read_msg_list = []

    def reader_counter(self):
        try:
            while True:
                msgId, msg, dlc, flg, time = self.ch1.read(timeout=200)
                msg_received = "".join("0x%02x " % b for b in msg)
                self.read_msg_list.append((time, msgId, msg_received))
        except:
            return self.read_msg_list

    def stop_reader(self):
        self.th_reader.cancel()


def grade_plane_actions(can_h):
    '''function for debug stage'''
    msg_clear_error = (0x2f, 0x02, 0x21, 0x01, 0x01, 0x00, 0x00, 0x00)
    msg_mode_speed = (0x2f, 0x03, 0x21, 0x00, 0x02, 0x00, 0x00, 0x00)#speed mode
    msg_set_speed = (0x23, 0x01, 0x22, 0x00, 0x1a, 0x4f, 0x00, 0x00)
    msg_break_on = (0x2f, 0x04, 0x21, 0x00, 0x00, 0x00, 0x00, 0x00)
    msg_set_heartbeat = (0x23, 0x16, 0x10, 0x01, 0xdc, 0x05, 0x64, 0x00)
    write_buffer = (msg_mode_speed, msg_set_speed, msg_break_on, msg_set_heartbeat, msg_clear_error)

    '''actions'''
    while True:
        can_h.send_msg([0x01, 0x00], 0x00)
        for msg in write_buffer:
            can_h.send_msg(msg, 0x601)
        sleep(0.020)
        can_h.send_msg([0x7F], 0x764)
        sleep(1)


if __name__ == '__main__':
    can_h = can_handler()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('hello.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Hello baby')

#     can_h.configure('CANOpen')
    can_h.configure()
    reader = periodic_reader(can_h, 0.2, logger)
    reader.start_to_read()
    sleep(5)
    reader.stop_reader()

    print '**** END PROGRAM ****'
