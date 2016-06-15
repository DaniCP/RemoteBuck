'''
Created on 1 de jun. de 2016

@author: daniel.cano
'''
import sys, os
from time import sleep
import time
from bitstring import BitString, BitArray
from threading import Thread

sys.path.append(os.getcwd() + '\..\..\CAN')
import can_handler
from validation_GreatPlains import greate_plains

def screen_loop():
    gp_motor_1.get_motor_current()
    gp_motor_2.get_motor_current()
    sleep(0.005)
    gp_motor_1.get_actual_speed()
    gp_motor_1.get_voltage()
    gp_motor_1.get_temperature()
    gp_motor_1.get_status()
    
    gp_motor_2.get_actual_speed()
    gp_motor_2.get_voltage()
    gp_motor_2.get_temperature()
    gp_motor_2.get_status()
    
    gp_motor_1.heartbeat_frame_send()
    sleep(0.4)

def screen_loop(can_h):
    print "enter in screen_loop"
    while True:
        can_h.send_msg([0x05], 0x764)
        
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x602)
        
        can_h.send_msg((0x40, 0x02, 0x22, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x00, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x02, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x00, 0x21, 0, 0, 0, 0, 0), 0x601)
        
        can_h.send_msg((0x40, 0x02, 0x22, 0, 0, 0, 0, 0), 0x602)
        can_h.send_msg((0x40, 0x00, 0x23, 0, 0, 0, 0, 0), 0x602)
        can_h.send_msg((0x40, 0x02, 0x23, 0, 0, 0, 0, 0), 0x602)
        can_h.send_msg((0x40, 0x00, 0x21, 0, 0, 0, 0, 0), 0x602)
        
        sleep(0.4)
        can_h.send_msg([0x05], 0x764)
        
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x602)
        sleep(0.4)
        
        
if __name__ == '__main__':
    ''' setup'''
    can_h = can_handler.can_handler()
    can_h.configure('CANOpen')
    gp_motor_1 = greate_plains(can_h, 0x601)
    gp_motor_2 = greate_plains(can_h, 0x602)
    
    gp_motor_1.set_operational()
    gp_motor_2.set_operational()
    
    gp_motor_1.set_heartbeat(1500)
    gp_motor_2.set_heartbeat(1500)        
#     gp_motor_1.heartbeat_start()
    gp_motor_1.heartbeat_frame_send()
    
    gp_motor_1.clear_errors()
    gp_motor_2.clear_errors()
    
    gp_motor_1.set_mode(2)
    gp_motor_2.set_mode(2)
    
    gp_motor_1.set_speed(20)
    gp_motor_2.set_speed(20)
    
    while True:
        can_h.send_msg([0x05], 0x764)
        
        can_h.reset_reader_counter()
        
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x602)
        
        can_h.send_msg((0x40, 0x02, 0x22, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x00, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x02, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x00, 0x21, 0, 0, 0, 0, 0), 0x601)
        
        can_h.send_msg((0x40, 0x02, 0x22, 0, 0, 0, 0, 0), 0x602)
        can_h.send_msg((0x40, 0x00, 0x23, 0, 0, 0, 0, 0), 0x602)
        can_h.send_msg((0x40, 0x02, 0x23, 0, 0, 0, 0, 0), 0x602)
        can_h.send_msg((0x40, 0x00, 0x21, 0, 0, 0, 0, 0), 0x602)
        
        sleep(0.4)
        can_h.send_msg([0x05], 0x764)
        
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x601)
        can_h.send_msg((0x40, 0x01, 0x23, 0, 0, 0, 0, 0), 0x602)
        sleep(0.4)
        
        list = can_h.reader_counter()
        if len(list) != 12:
            print time.ctime(), " no expected number of messages: ", len(list)
            print list
        
    ''' teardown'''
    gp_motor_1.set_speed(0)
#     gp_motor_1.heartbeat_stop()
    print '**** END PROGRAM ****'