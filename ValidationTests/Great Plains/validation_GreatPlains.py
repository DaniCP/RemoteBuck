# -*- coding: utf-8 -*-
import sys, os
from time import sleep
from bitstring import BitString, BitArray

sys.path.append(os.getcwd() + '\..\..\CAN') #anadir para linux
import can_handler

class greate_plains():
    def __init__(self, can_h, node_id):
        self.can_h = can_h
        self.node_id = node_id
        self.heartbeat = None
    
    def bytes(self, integer):
        '''usefull function to split high and low byte'''
        return divmod(integer, 0x100)
        
    def heartbeat_start(self):
        self.heartbeat = can_handler.periodic_frame_sender(can_h=can_h, period=1, msgId=0x764, msg=[0x7F])
        self.heartbeat.start_frame()
        
    def heartbeat_stop(self):
        self.heartbeat.stop_frame()
        
    def heartbeat_frame_send(self):
        self.can_h.send_msg(([0x7F]), 0x764)
    
    def set_operational(self):
        self.can_h.send_msg(([0x01, 0x00]), 0x00)
        
    def reset_node(self):
        '''to be implemented'''
        pass
        
    def clear_errors(self):
        self.can_h.send_msg((0x2f, 0x02, 0x21, 0x01, 0x01, 0x00, 0x00, 0x00), self.node_id)
        
    def set_brake(self, enable):
        '''enable shall be 1 or 0'''
        self.can_h.send_msg((0x2f, 0x04, 0x21, 0x00, enable, 0x00, 0x00, 0x00), self.node_id)        
    
    def set_heartbeat(self, time):
        '''time in ms'''
        high, low = self.bytes(time)
        self.can_h.send_msg((0x23, 0x16, 0x10, 0x01, low, high, 0x64, 0x00), self.node_id)

    def set_mode(self, mode):
        '''mode values:
            0 power off
            1 position mode
            2 speed mode'''
        self.can_h.send_msg((0x2f, 0x03, 0x21, 0x00, mode, 0x00, 0x00, 0x00), self.node_id)
        
    def set_speed(self,speed):
        '''speed argument in shaft'''
        speed_armature = speed * 81 * 10
        high, low = self.bytes(speed_armature)
        print hex(high), hex(low)
        self.can_h.send_msg((0x23, 0x01, 0x22, 0x00, low, high, 0x00, 0x00), self.node_id)
        
    def set_pos_target(self, pos):
        '''pos is the revolutions in shaft'''
        pos_armature = pos * 81
        high, low = self.bytes(pos_armature)
        self.can_h.send_msg((0x23, 0x7a, 0x60, 0x00, low, high, 0x00, 0x00), self.node_id)
        
class test():
    def __init__(self, can_h):
        self.can_h = can_h
        self.gp_obj = greate_plains(can_h, 0x601)
        
    def approx_Equal(self, x, y, tolerance):
        return abs(x-y) <= tolerance
    
    def setup(self):
        self.gp_obj.set_operational()
        self.gp_obj.set_heartbeat(1500)
        self.gp_obj.set_brake(0)
        self.gp_obj.heartbeat_start()
        self.gp_obj.clear_errors()        
    
    def teardown(self):
        self.gp_obj.set_speed(0)
        self.gp_obj.heartbeat_stop()
        
    def test1(self):
        '''doc: to check the boot-up message every 5sec'''        
        last_time = 0
        for i in range(0,3):
            msg, msgId, time = self.can_h.read_msg(timeout=-1)
            if (msgId == 0x701):
                diff_times = time - last_time
                last_time = time
                if (i>0):
#                     print "time between frames", diff_times
                    if (self.approx_Equal(diff_times, 5000, 100)):
                        print "PASS"
                    else:
                        print "FAIL"           
            else:
                i-=1
    def test2(self):
        '''doc: to check the boot-up message every 5sec'''        
        msg, msgId, time = self.can_h.read_msg(6000)
        if (msgId == 0x701):
            can_h.send_msg([0x01, 0x00], 0x00)# from pre-operational to operational
        '''to be completed'''   

    def test3(self):
        '''to cover issue GPSEEDER-1'''
        self.gp_obj.set_mode(1)#position mode
        self.gp_obj.set_speed(10)
        self.gp_obj.set_pos_target(5)      
        #start_time_to_target_reached()
        sleep(2)
        self.gp_obj.set_speed(60)
        #wait_till_target_reached and get speed from time: should be 30s, if it is less than 30s is fail (because accept speed change)

    def test4(self):
        self.gp_obj.set_mode(1)
        self.gp_obj.set_speed(30)
        self.gp_obj.set_pos_target(10)
        
if __name__ == '__main__':
    can_h = can_handler.can_handler()
    can_h.configure()

    test_obj = test(can_h)
#     while True:  
#     test_obj.setup()    
#     test_obj.test4()
#     sleep(4)
    
    '''test to execute: configure'''
    while True:
        test_obj.gp_obj.set_operational()
        test_obj.gp_obj.set_heartbeat(1500)
        test_obj.gp_obj.heartbeat_frame_send()
        test_obj.gp_obj.set_brake(0)        
        test_obj.gp_obj.clear_errors() 
          
        test_obj.gp_obj.set_mode(2)
        test_obj.gp_obj.set_speed(60)        
        sleep(1)
    
    '''teardown'''
#     test_obj.teardown()
    print '**** END PROGRAM ****'
