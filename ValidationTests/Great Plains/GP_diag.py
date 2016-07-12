'''
Created on 21 de jun. de 2016

@author: daniel.cano
'''
# -*- coding: utf-8 -*-
import sys, os
from time import sleep
import time
from bitstring import BitString, BitArray

sys.path.append(os.getcwd() + '\..\..\CAN')
import can_handler
from validation_GreatPlains import greate_plains


def request_diagnostic(node_id =2, rx_id=0x582, diag_id=0x0000):
    can_h.reader.add_subscriber(rx_id)
    high, low = divmod(diag_id, 0x100)
    can_h.send_msg((0x40, low, high, 0x00, 00, 00, 0x00, 0x00), 0x600+node_id)
    try:
        tp_message = can_h.reader.rx_diag_queue.get(timeout = 3)
        if tp_message != None:
            print 'Received data through TP layer:', tp_message
    except:
        print('Timeout expired when waiting for diagnostic answer!')
    finally:
        can_h.reader.remove_subscriber(rx_id=rx_id)
        
    return tp_message


if __name__ == '__main__':
    can_h = can_handler.can_handler()
    can_h.configure('CANOpen')
    
    msg = request_diagnostic(rx_id=0x582, diag_id=0x2201)
     
    sleep(4)
    del can_h
    print 'END'
