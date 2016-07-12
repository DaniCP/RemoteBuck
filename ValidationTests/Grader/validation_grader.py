# -*- coding: utf-8 -*-
import sys, os
from time import sleep
from bitstring import BitString, BitArray

sys.path.append(os.getcwd() + '\..\..\CAN')
import can_handler


class OWW():
    '''Class to manage the wiper (CAT Grader)
        PGN 64973 (0x1CFDCD00)'''
    def __init__(self, can_han):
        self.can_h = can_han
        self.id_ = 64973
        self.frontOperatorWiperSwitch = BitArray(bin='0001')        #_2863,4,1,4,U,15,0,1,0.000000,1.000000,,
        self.FrontNonOperatorWiperSwitch = BitArray(bin='0000')     #_2864,4,1,0,U,15,0,1,0.000000,1.000000,,
        self.RearWiperSwitch = BitArray(bin='0000')                 #_2865,4,2,4,U,15,0,1,0.000000,1.000000,,

        self.FrontOperatorWasherSwitch = BitArray(bin='000')        #_2866,3,6,5,U,7,0,1,0.000000,1.000000,,
        self.FrontNonOperatorWasherSwitch = BitArray(bin='000')     #_2867,3,6,2,U,7,0,1,0.000000,1.000000,,
        self.RearWasherFunction = BitArray(bin='000')               #_2868,3,7,5,U,7,0,1,0.000000,1.000000,,

        self.FrontOperatorWiperDelayControl = BitArray(bin='00000000')      #_2869,8,3,0,U,255,0,1,0.000000,0.400000,%,
        self.FrontNonOperatorWiperDelayControl = BitArray(bin='00000000')   #_2870,8,4,0,U,255,0,1,0.000000,0.400000,%,
        self.RearWiperDelayControl = BitArray(bin='00000000')               #_2871,8,5,0,U,255,0,1,0.000000,0.400000,%,
        self.pgn = can_handler.periodic_frame_sender(can_h=can_h, period=0.5,
                                                msgId=0x1CFDCD00, msg=self.prepare_msg())
        pgn.start_frame()

    def update_operator(self, spn_name, spn_value):

        self.pgn.msg = self.prepare_msg()

    def prepare_msg(self):
        by0 = (self.frontOperatorWiperSwitch + self.FrontNonOperatorWiperSwitch).uint
        by1 = (self.RearWiperSwitch + BitArray(bin='0000')).uint
        by2 = (self.FrontOperatorWiperDelayControl).uint
        by3 = (self.FrontNonOperatorWiperDelayControl).uint
        by4 = (self.RearWiperDelayControl).uint
        by5 = (self.FrontOperatorWasherSwitch + self.FrontNonOperatorWasherSwitch + BitArray(bin='00')).uint
        by6 = (self.RearWasherFunction + BitArray(bin='00000')).uint
        by7 = 0
        msg = (by0, by1, by2, by3, by4, by5, by6, by7)
        return msg

    def stop(self):
        self.pgn.stop_frame()

if __name__ == '__main__':
    can_h = can_handler.can_handler()
    can_h.configure()
    operator_wiper = OWW(can_h)
    """bus interaction"""

    msg = operator_wiper.prepare_msg()
    print msg
    pgn = can_handler.periodic_frame_sender(can_h=can_h, period=0.5,
                                                msgId=0x1CFDCD00, msg=msg)
#     =[0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    pgn.start_frame()

    sleep(5)
    pgn.msg = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
    sleep(2)
    pgn.stop_frame()
    sleep(2)
    print '**** END PROGRAM ****'
