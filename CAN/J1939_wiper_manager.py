'''
Created on 22 de jun. de 2016

@author: daniel.cano
'''
# -*- coding: utf-8 -*-
import sys, os
from time import sleep
import time
from bitstring import BitString, BitArray
import threading
import Transport_Protocol

# sys.path.append(os.getcwd() + '\..\..\CAN')
import can_handler

OFF = BitArray(hex='0x0')
LOW = BitArray(hex='0x1')
MEDIUM = BitArray(hex='0x2')
HIGH = BitArray(hex='0x3')
DELAYED1 = BitArray(hex='0x4')
DELAYED2 = BitArray(hex='0x5')
NOT_AVAILABLE = BitArray(hex='0xF')

WASH_OFF = BitArray(bin='000')
WASH_ON = BitArray(bin='001')
WASH_MEDIUM = BitArray(bin='010')
WASH_HIGH = BitArray(bin='011')
WASH_NOT_AVAILABLE = BitArray(bin='111')

class OWW():
    '''Class to manage the wiper J1939 compatible
        PGN 64973 (0xFDCD)'''
    def __init__(self):
        self.can_h = can_handler.can_handler()
        self.can_h.configure('J1939')
        self.id_ = 64973  # 0x18 FDCD 00
        self.rx_can_id = 0x18FDCDEB

        self.frontOperatorWiperSwitch = BitArray(bin='0000')        #_2863,4,1,4,U,15,0,1,0.000000,1.000000,,
        self.FrontNonOperatorWiperSwitch = BitArray(bin='0000')     #_2864,4,1,0,U,15,0,1,0.000000,1.000000,,
        self.RearWiperSwitch = BitArray(bin='0000')                 #_2865,4,2,4,U,15,0,1,0.000000,1.000000,,

        self.FrontOperatorWasherSwitch = BitArray(bin='000')        #_2866,3,6,5,U,7,0,1,0.000000,1.000000,,
        self.FrontNonOperatorWasherSwitch = BitArray(bin='000')     #_2867,3,6,2,U,7,0,1,0.000000,1.000000,,
        self.RearWasherFunction = BitArray(bin='000')               #_2868,3,7,5,U,7,0,1,0.000000,1.000000,,

        self.FrontOperatorWiperDelayControl = BitArray(bin='00000000')      #_2869,8,3,0,U,255,0,1,0.000000,0.400000,%,
        self.FrontNonOperatorWiperDelayControl = BitArray(bin='00000000')   #_2870,8,4,0,U,255,0,1,0.000000,0.400000,%,
        self.RearWiperDelayControl = BitArray(bin='00000000')               #_2871,8,5,0,U,255,0,1,0.000000,0.400000,%,

        self.pgn = can_handler.periodic_frame_sender(can_h=self.can_h,
                                                     period=0.5, msgId=0x18FDCD00,
                                                     msg=self.encode_msg())
        self.pgn.start_frame()
        # echo checker
#         self.can_h.reader.add_subscriber(rx_id=self.rx_can_id)
#         self.echo_checker()

    def update_operator(self):

        self.pgn.msg = self.encode_msg()

    def encode_msg(self):
        by0 = (self.frontOperatorWiperSwitch + self.FrontNonOperatorWiperSwitch).uint
        by1 = (self.RearWiperSwitch + BitArray(bin='0000')).uint
        by2 = (self.FrontOperatorWiperDelayControl).uint
        by3 = (self.FrontNonOperatorWiperDelayControl).uint
        by4 = (self.RearWiperDelayControl).uint
        by5 = (self.FrontOperatorWasherSwitch + self.FrontNonOperatorWasherSwitch + BitArray(bin='00')).uint
        by6 = (self.RearWasherFunction + BitArray(bin='00000')).uint
        by7 = 0
        msg = (by0, by1, by2, by3, by4, by5, by6, by7)
        print 'encode msg: ', msg
        return msg

    def stop(self):
        print 'stop pgn, broadcast, reader'
        self.pgn.stop_frame()
#         self.th_periodic.cancel()
        if hasattr(self, 'broadcast'):
            self.broadcast.stop_frame()
        self.can_h.__del__()

    def broadcast_setup(self, dest_add='0xff', src_add='0x00'):
        msgId = BitArray(BitArray('0x18DF')+BitArray(dest_add)+BitArray(src_add))
        self.can_h.send_msg([0x00, 0x00, 0x3F, 0xFF, 0xFF,
                             0xFF, 0xFF, 0xFF], msgId=msgId.int)

    def start_hold_broadcast(self):
        self.broadcast.stop_frame()

    def stop_hold_broadcast(self, dest_add='0xff', src_add='0x00'):
        msgId = BitArray(BitArray('0x18DF')+BitArray(dest_add)+BitArray(src_add))
        self.broadcast = can_handler.periodic_frame_sender(can_h=self.can_h,
                                                           period=5,
                                                           msgId=msgId.int,
                                                           msg=[0xFF, 0xFF,
                                                                0xFF, 0x0F,
                                                                0xFF, 0xFF,
                                                                0xFF, 0xFF])
        self.broadcast.start_frame()

    def echo_checker(self):
        try:
            while not self.can_h.reader.rx_diag_queue.empty():
                tp_message = self.can_h.reader.rx_diag_queue.get(timeout=3)
                if tp_message is not None:
                    print 'Received data through TP layer:', tp_message
#                 decode_msg(tp_message)
                else:
                    print 'not msg received'
        except:
            print('Timeout expired when waiting for echo message!')
        finally:
            self.th_periodic = threading.Timer(0.1, self.echo_checker)
            self.th_periodic.start()

    def request_diagnostic(self, node_id=2, rx_id=0x582, diag_id=0x0000):
        self.can_h.reader.add_subscriber(rx_id)
        high, low = divmod(diag_id, 0x100)
        self.can_h.send_msg((0x40, low, high, 0x00, 00, 00, 0x00, 0x00), 0x600+node_id)
        try:
            tp_message = self.can_h.reader.rx_diag_queue.get(timeout = 3)
            if tp_message != None:
                print 'Received data through TP layer:', tp_message
        except:
            print('Timeout expired when waiting for diagnostic answer!')
        finally:
            self.can_h.reader.remove_subscriber(rx_id=rx_id)

        return tp_message


class Diag_Manager():
    TOOL_ID = '0xFC'
    PGN_DM14 = '0xD9'
    PGN_DM15 = '0xD8'
    PGN_DM16 = '0xD7'

    CMD_ERASE = '0b000'
    CMD_READ = '0b001'
    CMD_WRITE = '0b010'
    CMD_OP_COMPLETED = '0b100'
    CMD_OP_FAIL = '0b101'

    P_TYPE_DIRECT = '0b0'
    P_TYPE_SPATIAL = '0b1'

    STATUS_PROCEED = BitString('0b000')
    STATUS_BUSY = BitString('0b001')
    STATUS_COMPLETE = BitString('0b100')
    STATUS_FAILED = BitString('0b101')

    def __init__(self, can_h):
        self.can_h = can_h
        self.tp = Transport_Protocol.Transport_Protocol(self)
        self._psw = '0xD204'

    def _wait_for_id(self, _id, timeout=10):
        t_start = time.time()
        msg, msgId, _time = self.can_h.read_msg(timeout*1000)
        while not (msgId == _id):
            try:
                msg, msgId, _time = self.can_h.read_msg()
                if time.time()-t_start > timeout:
                    print 'timeout waiting for id', _id, time.time()-t_start
                    return 0
#                     break
            except:
                print 'exception waiting for id: ', _id
                sleep(0.05)
                pass
        return msg

    def _id_composer(self, priority='0x07', _pgn='0xD9', dest_add='0xEB',
                     src_add=TOOL_ID):
        priority = BitString(priority)[-3:]
        reserved = BitString('0b0')
        dataPage = BitString('0b0')
        _id = priority + reserved + dataPage + BitString(_pgn) + BitString(dest_add) + BitString(src_add)
        return _id.uint

    def dm14_composer(self, length='0b00000000001', p_type=P_TYPE_SPATIAL,
                      cmd=CMD_READ, _spn='0x000000', p_extension='0x00',
                      _psw='0x04D2', _src=TOOL_ID):
        ''' Memory access request'''
        by1 = BitString(length)[-8:].uint
        by2 = (BitString(length)[:-8] + BitString(p_type) + BitString(cmd) + '0b1').uint
        by3 = BitString(_spn)[-8:].uint
        by4 = BitString(_spn)[-16:-8].uint
        by5 = BitString(_spn)[-24:-16].uint
        by6 = BitString(p_extension).uint
        by7 = BitString(_psw)[-8:].uint
        by8 = BitString(_psw)[:-8].uint

        msg = (by1, by2, by3, by4, by5, by6, by7, by8)
        self.can_h.send_msg(msg=msg, msgId=self._id_composer(_pgn=self.PGN_DM14, src_add=_src))

    def dm15_composer(self, length='0b00000000000', status=STATUS_COMPLETE, error_indicator='0xffffff', edcp_extension='0x00', seed='0x0000', _src=TOOL_ID):
        ''' Memory access response'''
        by1 = BitString(length)[-8:].uint
        by2 = (BitString(length)[:-8]+'0b0'+BitString(status)+'0b0').uint
        by3 = BitString(error_indicator)[-8:].uint
        by4 = BitString(error_indicator)[-16:-8].uint
        by5 = BitString(error_indicator)[-24:-16].uint
        by6 = BitString(edcp_extension).uint
        by7 = BitString(seed)[-8:].uint
        by8 = BitString(seed)[:-8].uint

        msg = (by1, by2, by3, by4, by5, by6, by7, by8)
        self.can_h.send_msg(msg=msg, msgId=self._id_composer(_pgn=self.PGN_DM15, src_add=_src))

    def dm15_decoder(self, msg):
        msg = BitString(msg)
        length = msg[8:11] + msg[:8]
        status = msg[12:15]
        error_indicator = msg[16:40]
        edcp_extension = msg[40:48]
#         print ('length: ', length, ' status: ', status, ' error: ',
#                error_indicator, ' edcp_extension: ', edcp_extension)

        if status == self.STATUS_PROCEED:
            print('proceed, length: %s' % length)
        elif status == self.STATUS_BUSY:
            print('busy, error: %s' % error_indicator)
        elif status == self.STATUS_COMPLETE:
            print('complete, length: %s' % length)
        elif status == self.STATUS_FAILED:
            print('Failed, error: %s' % error_indicator)

        return status, length, error_indicator

    def dm16_decoder(self, msg):
        msg = BitString(msg)
        len = msg[:8].uint
        data = msg[8:8*len+8]
        not_used = msg[8*len+8:]
        return data, not_used

    def dm16_composer(self, msg, _src=TOOL_ID):
        ''' msg should be a str '''
        msg = BitString(msg)
        if ((msg.len%8) != 0 or msg.len > 8*8): # debe ser multiplo de 8 y menor que 7
            print 'incorrect len:', msg.len
            raise Exception
        else:
            msg = BitString(uint=msg.len/8, length=8) + msg
            while msg.len < 8*8:
                msg.append(BitString('0b1'))
        msg = (msg[:8].uint, msg[8:16].uint, msg[16:24].uint, msg[24:32].uint,
               msg[32:40].uint, msg[40:48].uint, msg[48:56].uint, msg[56:64].uint)
        self.can_h.send_msg(msg=msg, msgId=self._id_composer(_pgn=self.PGN_DM16, src_add=_src))

    def commanded_address_composer(self, id_num, manuf_code, Func_inst,
                                   ecu_inst, func, vcl_sys, aac, ig, vsi,
                                   new_SA):
        ''' 9By PGN 0xFeD8 (through TP Broadcast)'''
        pass


class Katana():
    DELAY_CONTINUOUS = BitArray(bin='00000000')
    DELAY_STOP = BitArray(bin='11111011')
    DELAY_NOT_AVAILABLE = BitArray(bin='11111111')

    def __init__(self):
        self.wiper = OWW()

    def __del__(self):
        print 'delete katana'
        self.wiper.stop()

    def _reset(self, dest_add='0xeb'):
        msgId = BitArray(BitArray('0x18D6')+BitArray(dest_add)+'0xFC')
        self.wiper.can_h.send_msg([0x06, 00, 00, 00, 00, 00, 00, 00], msgId.int)  # reset command sigma
        sleep(4)

    def set_speed(self, speed=OFF):
        self.wiper.frontOperatorWiperSwitch = speed
        self.wiper.update_operator()

    def set_washer(self, cmd=WASH_OFF):
        self.wiper.FrontOperatorWasherSwitch = cmd
        self.wiper.update_operator()

    def calculate_delay_perc(self, perc=0.4):
        ''' input: int 0.4-100
            output: bitstring 00000001 is 0,4%
                              11111010 is 100%
        '''
        perc = perc * 0b11111010 / 100
        return BitString(uint=int(perc), length=8)

    def set_delay_percentage(self, delay=DELAY_STOP):
        self.wiper.FrontOperatorWiperDelayControl = delay
        self.wiper.update_operator()

if __name__ == '__main__':
    wiper = Katana()
    diag = Diag_Manager(wiper.wiper.can_h)

    diag.dm14_composer(_spn='0x000B15', cmd=diag.CMD_WRITE)
    sleep(0.5)
    rx = diag._wait_for_id('0x18d8fceb')
    diag.dm15_decoder(rx)
    diag.dm16_composer('0xaabbccdd')
    rx = diag._wait_for_id('0x18d8fceb')
    diag.dm15_decoder(rx)

    sleep(2)
    del wiper
    print 'END'

