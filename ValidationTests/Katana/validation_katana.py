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
import ctypes
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
                tp_message = self.kat.wiper.can_h.reader.rx_diag_queue.get(
                                                                timeout=3)
                if tp_message is not None:
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
        gap = self.get_time_gap()/1000.0
        print 'gap:', gap
        assert gap > 20, 'wrong message time gap: %f seconds' % gap

    def _test_DM13_wrong_dest(self):
        ''' Negative test: should ignore the "setup and hold" signals'''
        self.kat.set_speed(J1939_wiper_manager.LOW)
        sleep(1)
        self.kat.wiper.broadcast_setup(dest_add='0xcc', src_add='0x00')
        self.kat.wiper.stop_hold_broadcast(dest_add='0xCC')
        sleep(10)
        self.kat.wiper.start_hold_broadcast()
        self.kat.set_speed(J1939_wiper_manager.OFF)
        sleep(6)
        gap = self.get_time_gap()
        print 'gap:', gap
        assert gap/1000.0 < 1, 'wrong message time gap: %f seconds' % gap/1000

    def _test_DM13_wrong_hold_msg_dest(self):
        ''' Negative test: should ignore the "hold" signals but stop comm about 5s'''
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

    def compose_identity_name(self):
        arb_add = BitString('0b0')
        ind_group = BitString('0b001')
        vehic_sys_instance = BitString('0b0000')
        vehic_sys = BitString('0b0000001')
        reserved = BitString('0b0')
        func = BitString('0xff')
        func_instance = BitString('0b00000')
        ecu_instance = BitString('0b000')
        manuf_code = BitString('0b00110010010')
        identity_num = BitString('0b000000000000000000000')

        msg_str = arb_add+ind_group+vehic_sys_instance+vehic_sys+reserved+func+func_instance+ecu_instance+manuf_code+identity_num
#         by0 = msg_str[:8].uint
#         by1 = msg_str[8*2:8*3].uint
#         by2 = msg_str[8*3:8*4].uint
#         by3 = msg_str[8*4:8*5].uint
#         by4 = msg_str[8*5:8*6].uint
#         by5 = msg_str[8*6:8*7].uint
#         by6 = msg_str[8*7:8*8].uint
#         by7 = msg_str[8*8:8*9].uint
#         msg = (by0, by1, by2, by3, by4, by5, by6, by7)
        return msg_str

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
        '''memory write with security using dm16: Binary Data transfer
        - nominal test (figure App layer E.6)'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.diag.dm16_composer('0x11223344')
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_OP_COMPLETED)

        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_COMPLETE)
#         self.diag.dm15_composer(status=self.diag.STATUS_COMPLETE, _src=self.diag.TOOL_ID)
#         self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_OP_COMPLETED)
        self.kat.wiper.can_h.send_msg(msgId=0x18EAEBFC, msg=[0x00, 0xEE, 0x00])
        assert BitString('0x1122') == BitString(self.diag._wait_for_id('0x18eeffeb'))[:8*2]

    def _test_Name_id_num_read(self):
        '''read access allowed'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_READ)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_PROCEED), 'dm15 status: %s not expected, should be %s' % (status, self.diag.STATUS_PROCEED)        
        rx = self.diag._wait_for_id('0x18d7fceb')
        data, not_used = self.diag.dm16_decoder(rx)
        for char in not_used:
            assert char == 1, 'extra data in dm16 is: %s' % not_used
        rx = self.diag._wait_for_id('0x18d8fceb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_COMPLETE), 'dm15 status: %s not expected, should be %s' % (status, self.diag.STATUS_COMPLETE)

    def _test_Name_id_num_erase(self):
        '''No erase access allowed'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_ERASE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_BUSY) or status == BitString(self.diag.STATUS_FAILED), 'dm15 status: %s not expected, should be %s or %s' % (status, self.diag.STATUS_FAILED, self.diag.STATUS_BUSY)

    def _test_Name_Identity_Number_write_wrong_psw(self):
        '''memory write with security using transport layer
            - wrong password'''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _psw='0x04D3')
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_BUSY)

    def _test_Name_Identity_Number_write_spnPlus1(self):
        '''memory write with security using transport layer
            - wrong password'''
        self.diag.dm14_composer(_spn='0x000B16', cmd=self.diag.CMD_WRITE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_BUSY)

    def _test_send_op_completed_before_receive_it_from_ECU(self):
        '''figure E.3
        memory write with security using transport layer
        '''
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE)
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.diag.dm16_composer('0xaabbccdd')
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_OP_COMPLETED)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_COMPLETE)
        # check if is still operative
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.kat._reset()

    def _test_try_to_write_from_no_authenticated_address(self):
        '''memory write by no authenticated address during open connection'''
        tool_add1 = '0xFC'
        tool_add2 = '0xFD'
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _src=tool_add1)   # abro conexion desde tool1
        sleep(0.5)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.diag.dm16_composer('0xffffffff', _src=tool_add2)   # intento escribir desde una no verificada(tool2)
        rx = self.diag._wait_for_id('0x18d8fceb')
#         assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_BUSY)    # no deberia dejarme
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_OP_COMPLETED, _src=tool_add1)    # cierro la conexion abierta
        self.kat.wiper.can_h.send_msg(msgId=0x18EAEBFC, msg=[0x00, 0xEE, 0x00])
        assert BitString('0xaabb') == BitString(self.diag._wait_for_id('0x18eeffeb'))[:8*2] # compruebo que no me ha dejado escribir

    def _test_try_open_two_MA_connections(self):
        '''MA request from other address during open connection'''
        tool_add1 = '0xFC'
        tool_add2 = '0xFD'
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _src=tool_add1)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _src=tool_add2)   # intento abrir otra sesion
        rx = self.diag._wait_for_id('0x18d8fdeb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_BUSY), 'dm15 status: %s not expected, should be %s or %s' % (status, self.diag.STATUS_FAILED, self.diag.STATUS_BUSY)    # no deberia dejarme
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_OP_COMPLETED, _src=tool_add1)    # cerrar conexion

    def _test_try_open_new_MA_connection_after_wrong_closed_one(self):
        '''MA request from other address during open connection'''
        tool_add1 = '0xFC'
        tool_add2 = '0xFD'
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _src=tool_add1)
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_PROCEED)
        self.diag.dm16_composer('0xaabbccdd')
        rx = self.diag._wait_for_id('0x18d8fceb')
        assert self.diag.dm15_decoder(rx)[0] == BitString(self.diag.STATUS_COMPLETE) # I wont send the dm14.complete
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _src=tool_add2)   # intento abrir otra sesion
        rx = self.diag._wait_for_id('0x18d8fdeb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_BUSY), 'dm15 status: %s not expected, should be %s or %s' % (status, self.diag.STATUS_FAILED, self.diag.STATUS_BUSY)    # no deberia dejarme
        sleep(5)    # despues del timeout deberia dejarme
        self.diag.dm14_composer(_spn='0x000B15', cmd=self.diag.CMD_WRITE, _src=tool_add2)   # intento abrir otra sesion
        rx = self.diag._wait_for_id('0x18d8fdeb')
        status = self.diag.dm15_decoder(rx)[0]
        assert status == BitString(self.diag.STATUS_PROCEED), 'dm15 status: %s not expected, should be %s or %s' % (status, self.diag.STATUS_FAILED, self.diag.STATUS_BUSY)    # no deberia dejarme

    '''ECU SW Number'''
    def _test_ECU_Soft_number_nominal(self):
        self.diag.dm14_composer(_spn='0x000B56', cmd=self.diag.CMD_READ)
        status = self.diag.dm15_decoder(self.diag._wait_for_id('0x18d8fceb'))[0]
        assert status == BitString(self.diag.STATUS_PROCEED), (
               'dm15 status: %s not expected, should be %s' % (
                status, self.diag.STATUS_PROCEED))

        data = self.diag.tp.receive_data(src_add='0xEB', dest_add='0xFC')[8:]  # Transport Protocol
        assert str(data.hex).decode('hex') == '10014525500c', 'SW number not correct: %s' % str(data.hex).decode('hex')

        status = self.diag.dm15_decoder(self.diag._wait_for_id('0x18d8fceb'))[0]
        assert status == BitString(self.diag.STATUS_COMPLETE), (
                'dm15 status: %s not expected, should be %s' % (
                status, self.diag.STATUS_COMPLETE))

        self.diag.dm14_composer(_spn='0x000B56', cmd=self.diag.CMD_OP_COMPLETED)
        sleep(1)

    def _test_ECU_Soft_number_not_ack(self):
        self.diag.dm14_composer(_spn='0x000B56', cmd=self.diag.CMD_READ)
        status = self.diag.dm15_decoder(self.diag._wait_for_id('0x18d8fceb'))[0]
        assert status == BitString(self.diag.STATUS_PROCEED), (
               'dm15 status: %s not expected, should be %s' % (
                status, self.diag.STATUS_PROCEED))

        print self.diag.tp.receive_data_and_dont_send_ack(src_add='0xEB', dest_add='0xFC')  # Transport Protocol

        status = self.diag.dm15_decoder(self.diag._wait_for_id('0x18d8fceb'))[0]
        assert status == BitString(self.diag.STATUS_FAILED), (
                'dm15 status: %s not expected, should be %s' % (
                status, self.diag.STATUS_FAILED))

        self.diag.dm14_composer(_spn='0x000B56', cmd=self.diag.CMD_OP_FAIL)
        sleep(1)


class NetworkManagementTestClass(unittest.TestCase):

    def setUp(self):
        self.kat = J1939_wiper_manager.Katana()
        self.diag = J1939_wiper_manager.Diag_Manager(self.kat.wiper.can_h)

    def tearDown(self):
        del self.kat
        sleep(1)

    def request_identity_number(self):
        self.kat.wiper.can_h.send_msg(msgId=0x18EAFFFC, msg=[0x00, 0xEE, 0x00]) # request ACL
        msg = self.diag._wait_for_id('0x18eeffeb')
        id_num = msg[:4]
#         print "".join("0x%02x " % b for b in msg)
        return id_num

    def set_new_src_add(self, id_num, new_address):
        new_address = BitString(new_address)
        self.kat.wiper.can_h.send_msg([0x20, 0x09, 0x00, 0x02, 0xff, 0xd8,
                                       0xfe, 0x00], 0x18ecfffc) # bam
        self.kat.wiper.can_h.send_msg([0x01, id_num[0], id_num[1], id_num[2], id_num[3], 0x00,
                                       0x42, 0x00], 0x18ebfffc)
        self.kat.wiper.can_h.send_msg([0x02, 0x00, new_address.uint, 0xff, 0xff, 0xff,
                                       0xff, 0xff], 0x18ebfffc)
        sleep(3)

    '''Commanded Address'''
    def test_commanded_address(self):
        '''Nominal case:
            1)simulate high priority node with same src address 
                -> wiper should move to "cannot claim address" state
            2)commanded address
        '''
        id_num = self.request_identity_number()
        prior_can_id = self.diag._id_composer(priority='0x05', _pgn='0xEE', dest_add='0xFF',src_add='0xEB')
        self.kat.wiper.can_h.send_msg([0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                       0x00, 0x00], prior_can_id)
        assert self.diag._wait_for_id('0x18eefffe') != 0  # wait for cannot claim address
        # commanded address
        new_address = BitString('0xEC')
        self.kat.wiper.can_h.send_msg([0x20, 0x09, 0x00, 0x02, 0xff, 0xd8,
                                       0xfe, 0x00], 0x18ecfffc) # bam
        self.kat.wiper.can_h.send_msg([0x01, id_num[0], id_num[1], id_num[2], id_num[3], 0x00,
                                       0x42, 0x00], 0x18ebfffc)
        self.kat.wiper.can_h.send_msg([0x02, 0x00, new_address.uint, 0xff, 0xff, 0xff,
                                       0xff, 0xff], 0x18ebfffc)
        sleep(3)
        self.kat.wiper.can_h.send_msg(msgId=0x18EAFFFC, msg=[0x00, 0xEE, 0x00]) # request ACL
        assert self.diag._wait_for_id('0x18eeffec') != 0, 'timeout , ACL from EC not received'

        self.kat._reset(dest_add=new_address)

    def test_commanded_address_not_allowed(self):
        '''Negative case:
            In state "sending and receiving normal message traffic" commanded address isnt allowed 
        '''
        id_num = self.request_identity_number()
        new_address = BitString('0xEC')
        self.kat.wiper.can_h.send_msg([0x20, 0x09, 0x00, 0x02, 0xff, 0xd8,
                                       0xfe, 0x00], 0x18ecfffc)
        self.kat.wiper.can_h.send_msg([0x01, id_num[0], id_num[1], id_num[2], id_num[3], 0x00,
                                       0x42, 0x00], 0x18ebfffc)
        self.kat.wiper.can_h.send_msg([0x02, 0x00, new_address.uint, 0xff, 0xff, 0xff,
                                       0xff, 0xff], 0x18ebfffc)

        self.kat.wiper.can_h.send_msg(msgId=0x18EAFFFC, msg=[0x00, 0xEE, 0x00]) # request ACL
        assert (self.diag._wait_for_id('0x18eeffeb')) != 0  # no timeout, still SA 0xEB

    def test_msg_with_same_src_address(self):
        '''In "successful in claiming add" received message with own SA
        acceptance criteria: Re-Claim current Address
        '''
        self.kat.wiper.can_h.send_msg(msgId=0x18FDCDEB, msg=[0x12, 0x34, 0x00]) # message with same SA
        assert (self.diag._wait_for_id('0x18eeffeb')) != 0  # received ACL from 0xEB.

    def test_contending_adrs_claim(self):
        '''
        '''
        id_num = self.request_identity_number()
        self.kat._reset()
        self.diag._wait_for_id(_id='0x18eeffeb', timeout=10)
        self.diag._wait_for_id(_id='0x18eeffeb', timeout=10)
        prior_can_id = self.diag._id_composer(priority='0x05', _pgn='0xEE', dest_add='0xFF',src_add='0xEB')
        self.kat.wiper.can_h.send_msg([0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                        0x00, 0x00], prior_can_id)
        assert self.diag._wait_for_id('0x18eefffe') != 0  # cannot claim address
        self.set_new_src_add(id_num, '0xEB')
        sleep(5)


class Functional(unittest.TestCase):
    ''' checkeo visual'''
    def setUp(self):
        self.kat = J1939_wiper_manager.Katana()
        self.diag = J1939_wiper_manager.Diag_Manager(self.kat.wiper.can_h)

    def tearDown(self):
        del self.kat
        sleep(1)

    def _test_whex_int(self):
        '''WHEX case
        '''
        self.kat.set_speed(J1939_wiper_manager.NOT_AVAILABLE)
        self.kat.set_delay_percentage(self.kat.calculate_delay_perc(1))    # 1% de 20s=0.2s
        sleep(4)
        self.kat.set_delay_percentage(self.kat.calculate_delay_perc(50))    # 50% de 20s=10s
        sleep(14)
        self.kat.set_delay_percentage(self.kat.calculate_delay_perc(100))    # 100% de 20s=20s
        sleep(24)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)    # stop
        sleep(2)

    def _test_whex_cont(self):
        '''WHEX SPN2869
        0000000 Continuous    Wiper motor runs in continuous mode.
        0000001 - 1111010 Delay    Wiper motor will operate with an intermittent time 1 - 100% of 20s
        111111011 off    Wiper motor stopped at parking position.
        11111111 Not Available
        '''
        self.kat.set_speed(J1939_wiper_manager.NOT_AVAILABLE)
        self.kat.set_delay_percentage(self.kat.DELAY_CONTINUOUS)    # cont
        sleep(5)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)    # stop
        sleep(2)

    def _test_whex_washer_timout(self):
        ''' test with broken hall sensor'''
        self.kat.set_speed(J1939_wiper_manager.NOT_AVAILABLE)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)
        self.kat.set_washer(J1939_wiper_manager.WASH_ON)
        sleep(2)
        self.kat.set_washer(J1939_wiper_manager.WASH_OFF)
        sleep(3)
        ctypes.windll.user32.MessageBoxA(0, 'deberia haber parado', '', 1)
        self.kat.set_delay_percentage(self.kat.DELAY_CONTINUOUS)    # cont
        sleep(5)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)    # stop
        ctypes.windll.user32.MessageBoxA(0, 'si ha arrancado y parado la proteccion es OK', '', 1)

    def _test_whex_washer_timout2(self):
        ''' test with broken hall sensor'''
        self.kat.set_speed(J1939_wiper_manager.NOT_AVAILABLE)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)
        self.kat.set_washer(J1939_wiper_manager.WASH_ON)
        sleep(2)
        self.kat.set_washer(J1939_wiper_manager.WASH_OFF)
        self.kat.set_delay_percentage(self.kat.DELAY_CONTINUOUS)    # cont
        sleep(15)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)    # stop
        ctypes.windll.user32.MessageBoxA(0, 'si ha parado es OK', '', 1)

    def _test_whex_washer_not_available(self):
        self.kat.set_washer(J1939_wiper_manager.WASH_NOT_AVAILABLE)
        self.kat.set_speed(J1939_wiper_manager.NOT_AVAILABLE)
        self.kat.set_delay_percentage(self.kat.DELAY_CONTINUOUS)    # cont
        sleep(6)
        self.kat.set_delay_percentage(self.kat.DELAY_STOP)    # stop
        sleep(2)

    def _test_thex_washer_not_available(self):
        self.kat.set_washer(J1939_wiper_manager.WASH_NOT_AVAILABLE)
        self.kat.set_delay_percentage(self.kat.DELAY_NOT_AVAILABLE)
        self.kat.set_speed(J1939_wiper_manager.LOW)
        sleep(7)
        self.kat.set_speed(J1939_wiper_manager.OFF)
        sleep(2)

    def _test_thex(self):
        '''THEX SPN2863: has continuous wiper movement and 3s & 6s intermittent
        0000 off    Wiper motor stopped at parking position.
        0001 Low    Wiper motor runs in continuous mode.
        0010 Medium    Function not available. Will be ignored.
        0011 High    Function not available. Will be ignored.
        0100 Delayed 1    Wiper motor will operate with an intermittent time of 3 seconds.
        0101 Delayed 2    Wiper motor will operate with an intermittent time of 6 seconds.
        1111 Not Available

        '''
        self.kat.set_delay_percentage(self.kat.DELAY_NOT_AVAILABLE)
        self.kat.set_speed(J1939_wiper_manager.LOW)
        sleep(7)
        self.kat.set_speed(J1939_wiper_manager.OFF)
        sleep(2)


if __name__ == '__main__':
    unittest.main()  # run all tests
    print 'END'
