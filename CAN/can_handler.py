#!/usr/bin/env python
import ctypes as ct
from bitstring import BitArray, Bits
import Queue
import logging
from time import sleep
import time
import threading
import os
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
        try:
            self.can_h.send_msg(self.msg, self.msgId)
            self.th_periodic = threading.Timer(self.period, self.start_frame)
            self.th_periodic.start()
        except:
            print 'exception starting the frame, msg:', self.msg
            self.th_periodic = threading.Timer(self.period, self.start_frame)
            self.th_periodic.start()

    def stop_frame(self):
        print 'stop periodic frame sender ID: %d' % self.msgId
        self.th_periodic.cancel()


class periodic_reader():
    def __init__(self, can_h=None, period=0.1):
        self.can_h = can_h
        self.period = period  # seconds
        self.th_periodic = None
        self.logger = None
        self.init_logger()
        self.read_buffer()

        self.rx_diag_queue = Queue.Queue()
        self.subscribers = []

    def __del__(self):
        print 'delete periodic reader'
        self.stop_reader()

    def init_logger(self):
        self.logger = logging.getLogger(__name__)
        if not os.path.exists('../logs/'):
            os.makedirs('../logs/')

        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('../logs/CANlog_' + time.strftime(
                                    "%Y_%m_%d_%H_%M_%S",
                                    time.gmtime(time.time())) + '.log')
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug('time, dlc, msgId, msg_received')

    def configure(self, period=None):
        self.can_h = can_h
        self.period = period

    def read_buffer(self):
        try:
            while True:
                msgId, msg, dlc, flg, time = self.can_h.ch1.read()
                msg_received = "".join("0x%02x " % b for b in msg)
                self.logger.debug('%s %s %s %s', time, dlc, hex(msgId), msg_received)
                for subscriber in self.subscribers:
                    if msgId == subscriber:
                        self.rx_diag_queue.put((time, msgId, msg_received))
        except:
            #             self.logger.warn('exception')
            self.th_periodic = threading.Timer(self.period, self.read_buffer)
            self.read_msg_list = []
            self.th_periodic.start()

    def start_to_read(self):
        self.read_buffer()

    def stop_reader(self):
        print 'stop reader'
        self.th_periodic.cancel()

    def add_subscriber(self, rx_id=0x701):
        self.subscribers.append(rx_id)

    def remove_subscriber(self, rx_id=0x701):
        self.subscribers.remove(rx_id)

    def remove_all_subscribers(self):
        self.subscribers = []

    def get_subscribers(self):
        return self.subscribers


class can_handler():
    def __init__(self):
        self.canLib = canlib.canlib()
#         self.configure()
        self.reader = periodic_reader(self, period=0.2)
        self.reader_period = 0.01 #seconds
        self.old_read_msg = ''
        self.read_msg_list = []
        self.flag = canlib.canMSG_EXT
        self.reader.stop_reader()

    def __del__(self):
        print 'can_h deleted'
        self.reader.stop_reader()

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
                    self.flag = canlib.canMSG_EXT
                elif bus_type == 'CANOpen':
                    self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_ACCEPT_VIRTUAL)
                    self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                    self.ch1.setBusParams(canlib.canBITRATE_125K)
                    self.flag = 0
                else:   # default J1939
                    self.ch1 = self.canLib.openChannel(0, canlib.canOPEN_REQUIRE_EXTENDED + canlib.canOPEN_ACCEPT_VIRTUAL)
                    self.ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
                    self.ch1.setBusParams(canlib.canBITRATE_250K)
                    self.flag = canlib.canMSG_EXT

                self.ch1.busOn()
            except (self.canlib.canError) as ex:
                print(ex)

    def send_msg(self, msg, msgId, flg=False):
        msg_writen = "".join("0x%02x " % b for b in msg)
        flg = self.flag
#         print "write: ", msg_writen
        try:
            self.ch1.write(msgId, msg, flg)
            sleep(0.001)
        except() as ex:
            print "**********    EXCEPTION WHILE WRITE    ***********"
            print ex
            sleep(0.3)
            self.ch1.busOff()
            self.ch1.close()
            self.configure()
            self.ch1.write(msgId, msg, flg)
#         except (self.canLib.canNoMsg) as ex:
#             None
#         except (self.canLib.canError) as ex:
#             print(ex)

    def read_msg(self, timeout=2000):
        try:
            msgId, msg, dlc, flg, time = self.ch1.read(timeout)
#         msg_received = "".join("0x%02x " % b for b in msg)
#         print 'read: ', msgId, msg, time
            return msg, hex(msgId), time
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
#     can_h.configure('CANOpen')
    can_h.configure()
    can_h.send_msg([0x06, 00, 00, 00, 00, 00, 00, 00], 0x1cd6fffc)  # reset command sigma
    sleep(5)
    can_h.reader.stop_reader()

    print '**** END PROGRAM ****'
