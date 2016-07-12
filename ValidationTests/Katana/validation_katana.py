'''
Created on 22 de jun. de 2016

@author: daniel.cano
'''
# -*- coding: utf-8 -*-
import unittest
import sys, os
from time import sleep
import time
from bitstring import BitString, BitArray
from _socket import timeout

sys.path.append(os.getcwd() + '\..\..\CAN')
import J1939_wiper_manager


class DM13(unittest.TestCase):

    def setUp(self):
        self.kat = J1939_wiper_manager.Katana()

    def tearDown(self):
        del self.kat

    def get_time_gap(self):
        last_time = 0
        greatest_gap_time = 0
        try:
            while not self.kat.wiper.can_h.reader.rx_diag_queue.empty():
                tp_message = self.kat.wiper.can_h.reader.rx_diag_queue.get(timeout=3)
                if tp_message is not None:
#                     print 'msg time', tp_message[0]
                    gap = tp_message[0] - last_time
                    last_time = tp_message[0]
                    if gap > greatest_gap_time:
                        greatest_gap_time = gap
                else:
                    print 'wrong msg received'
        except:
            print('Timeout expired when waiting for echo message!')
        finally:
            return greatest_gap_time

    def _test_DM13_broadcast_nominal(self):
        ''' Nominal test '''
        self.kat.set_speed(J1939_wiper_manager.LOW)
        sleep(1)
        self.kat.wiper.broadcast_setup()
        self.kat.wiper.stop_hold_broadcast()
        sleep(20)
        self.kat.wiper.start_hold_broadcast()
        self.kat.set_speed(J1939_wiper_manager.OFF)
        sleep(6)
        gap = self.get_time_gap()
        print 'gap:', gap
        assert gap/1000.0 > 20, 'wrong message time gap: %f seconds' % gap/1000

    def _test_DM13_wrong_dest(self):
        ''' Negative test: should ignore the "atup and hold" signals'''
        self.kat.set_speed(J1939_wiper_manager.LOW)
        sleep(1)
        self.kat.wiper.broadcast_setup()
        self.kat.wiper.stop_hold_broadcast(dest_add='0xCC')
        sleep(10)
        self.kat.wiper.start_hold_broadcast()
        self.kat.set_speed(J1939_wiper_manager.OFF)
        sleep(6)
        gap = self.get_time_gap()
        print 'gap:', gap
        assert gap/1000.0 < 1, 'wrong message time gap: %f seconds' % gap/1000

    def _test_DM13_wrong_hold_msg_dest(self):
        ''' Negative test: should ignore the "atup and hold" signals'''
        self.kat.set_speed(J1939_wiper_manager.LOW)
        sleep(1)
        self.kat.wiper.broadcast_setup(dest_add='0xEB')
        self.kat.wiper.stop_hold_broadcast(dest_add='0xCC')
        sleep(10)
        self.kat.wiper.start_hold_broadcast()
        self.kat.set_speed(J1939_wiper_manager.OFF)
        sleep(6)
        gap = self.get_time_gap()/1000.0
        print 'gap:', gap
        assert gap < 7 and gap > 5, 'wrong message time gap: %f seconds' % gap

    def _test_DM13_wrong_hold_values(self):
        pass

    def _test_DM13_wrong_setup_values(self):
        pass

    def _test_DM13_wrong_setup_dest(self):
        pass


class DM14_16(unittest.TestCase):

    def setUp(self):
        self.kat = J1939_wiper_manager.Katana()
        self.diag = J1939_wiper_manager.Diag_Manager(self.kat.wiper.can_h)

    def tearDown(self):
        del self.kat
        sleep(1)

    def req_resp(self, txId=0, txMsg=0, rxId=0):
        self.kat.wiper.can_h.reader.remove_all_subscribers()
        self.kat.wiper.can_h.reader.add_subscriber(rx_id=rxId)
        sleep(1)
        self.kat.wiper.can_h.send_msg(txMsg, txId)
        response = self.kat.wiper.can_h.reader.rx_diag_queue.get(timeout=3)
        print 'rx %s: ' % hex(response[1]), response
        return response
    '''Identity Number'''
    def _test_Name_Identity_Number_write(self):
        '''memory write with security using transport layer
            - nominal test'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x1cd8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.diag.dm16_composer('0xaabbccdd')
        rx = self.diag._wait_for_id('0x1cd8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_COMPLETE)
        self.kat.wiper.can_h.send_msg(msgId=0x1CEAEBFC, msg=[0x00, 0xEE, 0x00])
        assert BitString('0xaabb') == BitString(self.diag._wait_for_id('0x18eeffeb'))[:8*2]

    def _test_Name_id_num_read(self):
        '''No read access allowed????'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_READ)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x1cd8fceb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_BUSY) or status == BitString(self.diag.STATUS_FAILED), 'dm15 status: %s not expected, should be %s or %s' % (status, self.diag.STATUS_FAILED, self.diag.STATUS_BUSY)

    def _test_Name_id_num_erase(self):
        '''No erase access allowed'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_ERASE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x1cd8fceb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_BUSY) or status == BitString(self.diag.STATUS_FAILED), 'dm15 status: %s not expected, should be %s or %s' % (status, self.diag.STATUS_FAILED, self.diag.STATUS_BUSY)

    def _test_Name_Identity_Number_write_wrong_psw(self):
        '''memory write with security using transport layer
            - wrong password'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _psw='0x04D3')
        sleep(0.5)
        rx = self.diag._wait_for_id('0x1cd8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_BUSY)

    def _test_Name_Identity_Number_write_spnPlus1(self):
        '''memory write with security using transport layer
            - wrong password'''
        self.diag.dm14_composer(_spn='0x000B16', cmd=self.diag.CMD_WRITE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x1cd8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_BUSY)
    '''ECU SW Number'''
    def _test_ECU_Soft_number_nominal(self):
        self.diag.dm14_composer(_spn='0x000B56', cmd=self.diag.CMD_READ)
#         self.kat.wiper.can_h.send_msg(msgId=0x1CD9EBFC,msg=[0x01, 0x13, 0x56, 0x0b, 0x00, 0x00,0xd2, 0x04])
        sleep(0.05)
        print BitString(self.diag._wait_for_id('0x1cd8fceb'))
        print BitString(self.diag._wait_for_id('0x1cecfceb'))

        self.kat.wiper.can_h.send_msg(msgId=0x1CECEBFC, msg=[0x11, 0xff, 0x01,
                                                             0xff, 0xff, 0x00,
                                                             0xD7, 0x00])
        print self.diag._wait_for_id('0x1cebfceb')[0]
        print self.diag._wait_for_id('0x1cebfceb')[0]
        self.kat.wiper.can_h.send_msg([0x13, 0x0e, 0x00, 0x02, 0xff, 0x00,
                                       0xd7, 0x00], 0x1cecebfc)
        print self.diag._wait_for_id('0x1cd8fceb')[0]
        self.kat.wiper.can_h.send_msg([0x01, 0x19, 0x56, 0x0b, 0x00, 0x00,
                                       0xd2, 0x04], 0x1cd9ebfc)
        sleep(2)
    '''Commanded Address'''
    def _test_multiple_read_with_security(self):
        '''figure E.3'''
        pass
    def _test_commanded_addres(self):
        new_address = 0xEE
        self.kat.wiper.can_h.send_msg([0x20, 0x09, 0x00, 0x02, 0xff, 0xd8,
                                       0xfe, 0x00], 0x1cecfffc)
        self.kat.wiper.can_h.send_msg([0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                                       0xff, 0x00], 0x1cebfffc)
        self.kat.wiper.can_h.send_msg([0x02, 0x00, 0xEC, 0xff, 0xff, 0xff,
                                       0xff, 0xff], 0x1cebfffc)
        self.kat.wiper.can_h.send_msg(msgId=0x1CEAEBFC, msg=[0x00, new_address, 0x00])
        print self.diag._wait_for_id('0x18eeff'+str(new_address))


if __name__ == '__main__':
    unittest.main() # run all tests
    print 'END'
