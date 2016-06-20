# -*- coding: utf-8 -*-
import sys, os
from time import sleep
import time
from bitstring import BitString, BitArray
import matplotlib.pyplot as plt
import operator
from numpy import ERR_CALL
from compiler.ast import Node

sys.path.append(os.getcwd() + '\..\..\CAN')
import can_handler

class greate_plains():
    def __init__(self, can_h, node_id):
        self.can_h = can_h
        self.node_id = node_id
        self.response_id = 0x580 + node_id - 0x600
        self.heartbeat = None
    
    def setup(self):
        self.set_operational()
        self.set_heartbeat(1500)
        self.set_brake(0)
        self.heartbeat_start()
        self.clear_errors() 
        
    def bytes(self, integer):
        '''usefull function to split high and low byte'''
        return divmod(integer, 0x100)
        
    def heartbeat_start(self):
        self.heartbeat = can_handler.periodic_frame_sender(can_h=self.can_h, period=1, msgId=0x764, msg=[0x7F])
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
        speed_armature = int(speed * 81 * 10)
        high, low = self.bytes(speed_armature)
#         print hex(high), hex(low)
        self.can_h.send_msg((0x23, 0x01, 0x22, 0x00, low, high, 0x00, 0x00), self.node_id)
        
    def set_pos_target(self, pos):
        '''pos is the revolutions in shaft'''
        pos_armature = pos * 81
        high, low = self.bytes(pos_armature)
        self.can_h.send_msg((0x23, 0x7a, 0x60, 0x00, low, high, 0x00, 0x00), self.node_id)
        
    def get_motor_velocity_command(self):
        try:
            self.can_h.send_msg((0x40, 0x01, 0x22, 0x00, 00, 00, 0x00, 0x00), self.node_id)
            msg, msgId, time = self.can_h.read_msg()
            
            while not (msgId==self.response_id and msg[0]==0x43 and msg[1]==0x01 and msg[2]==0x22):
                try:
                    msg, msgId, time = self.can_h.read_msg()
                except:
                    speed = None
            
            speed = BitString("0x%02x " % msg[5])
            speed.append("0x%02x " % msg[4])
            return speed.uint/810.0
        except:
            return None
        
    def get_actual_speed(self):
        '''returned speed in shaft'''
        self.can_h.send_msg((0x40, 0x02, 0x22, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x43 and msg[1]==0x02 and msg[2]==0x22):
            try:
                msg, msgId, time = self.can_h.read_msg()
            except:
                speed = None
            
        speed = BitString("0x%02x " % msg[5])
        speed.append("0x%02x " % msg[4])
        return speed.uint/810.0
#         return speed.int
    
    def get_motor_current(self):
        '''returned in milliamperes '''
        self.can_h.send_msg((0x40, 0x01, 0x23, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x4b and msg[1]==0x01 and msg[2]==0x23):
            msg, msgId, time = self.can_h.read_msg()
            
        current = BitString("0x%02x " % msg[5])
        current.append("0x%02x " % msg[4])
        return current.uint
    
    def get_target_reached(self):
        '''returned true/false'''
        self.can_h.send_msg((0x40, 0x41, 0x60, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x4b and msg[1]==0x41 and msg[2]==0x60):
            msg, msgId, time = self.can_h.read_msg()
            
        target_reached = BitString("0x%02x " % msg[5]) 
        return target_reached.bin[5] 
   
    def get_actual_position(self):
        '''returned position in shaft'''
        self.can_h.send_msg((0x40, 0x64, 0x60, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x43 and msg[1]==0x64 and msg[2]==0x60):
            msg, msgId, time = self.can_h.read_msg()
            
        pos = BitString("0x%02x " % msg[5])
        pos.append("0x%02x " % msg[4])
        return pos.uint/81.0 
    
    def get_voltage(self):
        self.can_h.send_msg((0x40, 0x00, 0x23, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x4B and msg[1]==0x00 and msg[2]==0x23):
            msg, msgId, time = self.can_h.read_msg()
            
        voltage = BitString("0x%02x " % msg[5])
        voltage.append("0x%02x " % msg[4])
        return voltage.uint
    
    def get_temperature(self):
        self.can_h.send_msg((0x40, 0x02, 0x23, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x4B and msg[1]==0x02 and msg[2]==0x23):
            msg, msgId, time = self.can_h.read_msg()
            
        temp = BitString("0x%02x " % msg[5])
        temp.append("0x%02x " % msg[4])
        return temp.uint
    
    def get_status(self):
        self.can_h.send_msg((0x40, 0x00, 0x21, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = self.can_h.read_msg()
        
        while not (msgId==self.response_id and msg[0]==0x4B and msg[1]==0x00 and msg[2]==0x21):
            msg, msgId, time = self.can_h.read_msg()
            
        status = BitString("0x%02x " % msg[5])
        status.append("0x%02x " % msg[4])
        return status.uint
    
    def wait_till_error(self, timeout):
#         self.can_h.send_msg((0x40, 0x41, 0x60, 0x00, 00, 00, 0x00, 0x00), self.node_id)
        msg, msgId, time = None, None, None
        
        while not (msgId==0x081 and msg[0]==0x30 and msg[1]==0x81):
            msg, msgId, time = self.can_h.read_msg(timeout)
            
        error_code = BitString("0x%02x " % msg[1])
        error_code.append("0x%02x " % msg[0])
        return error_code
        
        
class test():
    def __init__(self, can_h, num_nodes):
        ''' constructor prepared to 2 Nodes. Not scalable yet '''
        self.can_h = can_h
        if num_nodes==1:
            self.gp_obj = greate_plains(can_h, 0x601)
            self.gp_obj2 = greate_plains(can_h, 0x602)
            self.gp_nodes_list = [self.gp_obj]
        elif num_nodes==2:
            self.gp_obj = greate_plains(can_h, 0x602)
            self.gp_obj2 = greate_plains(can_h, 0x601)
            self.gp_nodes_list = [self.gp_obj, self.gp_obj2]
        else:
            print 'num_nodes not allowed, only 1 or 2 supported'

        
    def approx_Equal(self, x, y, tolerance):
        return abs(x-y) <= tolerance
    
    def setup(self):
        for node in self.gp_nodes_list:
            node.setup()       
    
    def teardown(self):
        for node in self.gp_nodes_list:
            node.set_speed(0)
            node.heartbeat_stop()
        
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
               
    '''POSITION CONTROL TESTS'''
    def test_pos_1(self):
        '''to cover issue GPSEEDER-1
            changes during process are ignored 
            (not ignored, performed after finisth the first target)'''
        self.gp_obj.set_mode(1)#position mode
        self.gp_obj.set_speed(10)
        self.gp_obj.set_pos_target(5)      
        #start_time_to_target_reached()
        sleep(5)
        self.gp_obj.set_speed(60)
        self.gp_obj.set_pos_target(3)
        #wait_till_target_reached and get speed from time: should be 30s, if it is less than 30s is fail (because accept speed change)
        sleep(25)
        
    def test_pos_2(self):
        '''check max pos allowed is 5 rev'''
        self.gp_obj.set_mode(1)
        self.gp_obj.set_speed(30)
        self.gp_obj.set_pos_target(10)
        sleep(25)
    
    def periodic_test(self):
        while True:
            self.gp_obj.set_operational()
            self.gp_obj.set_heartbeat(1500)
            self.gp_obj.heartbeat_frame_send()
            self.gp_obj.set_brake(0)        
            self.gp_obj.clear_errors() 
              
            self.gp_obj.set_mode(2)
            self.gp_obj.set_speed(60)        
            sleep(1)
            
    def test_pos_3(self):
        '''to check the 60 rev/seg acceleration: use oscilloscope to measure stabilization current time'''
        self.gp_obj.set_mode(1)
        self.gp_obj.set_speed(60)
        for i in range(0,5):
            self.gp_obj.set_pos_target(2)
            sleep(3)

    def test_vel_1(self):
        '''check acceleration and command works'''
        self.gp_obj.set_mode(2)
        self.gp_obj.set_speed(30)
        sleep(5)
        self.gp_obj.set_speed(60)
        sleep(5)
        
    def test_vel_2(self):
        '''check target reached when +-2 rpm'''
        speed_target = 30
        self.gp_obj.set_mode(2)
        self.gp_obj.set_speed(speed_target)
        time_start = time.time()
        while not self.gp_obj.get_target_reached()=='1':
#             print time.time()
#             print self.gp_obj.get_actual_speed()
            sleep(0.050)
        actual_speed = self.gp_obj.get_actual_speed()
        time_spent = time.time() - time_start
        print "actual speed:", actual_speed, "accuracy: ", abs(speed_target - actual_speed)
        print "time spent to reach the target: ", time_spent
        
    def test_vel_new(self):
        '''investigando'''        
        self.gp_obj.set_mode(2)
        self.gp_obj.set_speed(30)
        sleep(5)
        for i in range(0,10):
            self.gp_obj.set_pos_target(5)
            sleep(1)
                    
        self.gp_obj.set_speed(0)
        print "now is stopped"
        self.gp_obj.set_mode(1)
        sleep(15)    
        
    '''CANOpen interface tests'''
    def test_interf_1(self):
        '''1080: check consumer heartbeat can be modified'''
        self.gp_obj.set_heartbeat(3000)
        sleep(5)
        self.gp_obj.heartbeat_stop()
        self.gp_obj.heartbeat_frame_send()
        time_start = time.time()
        error_code = self.gp_obj.wait_till_error(5000)
        print "time_spent: ", time.time() - time_start, "error code:", error_code, "\nshould be 3s and 0x8130"
        
    def test_interf_2(self):
        '''Node ID: 0x2000'''
        write_node_id2 = (0x2f, 0x00, 0x20, 0x00, 0x02, 0x00, 0x00)
        
    ''' VELOCITY CONTROL TESTS'''
    def test_speed_targets(self, targets_list=[], step_time=5, offset=0):
        TIME_INDX = 0
        VEL_INDX = 1
        TARGET_INDX = 2
        TARGET_REACH_INDX = 3
        MOTOR2_TARGET_OFFSET =  offset #RPM
        result_list = []
        
        for node in self.gp_nodes_list:
            result_list.append([ [], [], [], [] ])
        
        time_start = time.time()
        
        for target in targets_list:
            print 'cambio de velocidad, speed: ', target
            for node in self.gp_nodes_list:
                    node.set_mode(2)
                    if self.gp_nodes_list.index(node)==0:
                        node.set_speed(target)
                    else:
                        node.set_speed(target + MOTOR2_TARGET_OFFSET)
            
            start_step_time = time.time()
            while (time.time()-start_step_time < step_time):
                i = 0
                for node in self.gp_nodes_list:
                    result_list[i][TIME_INDX].append(time.time()-time_start)
                    result_list[i][VEL_INDX].append(node.get_actual_speed())
                    result_list[i][TARGET_INDX].append(node.get_motor_velocity_command())
                    result_list[i][TARGET_REACH_INDX].append(self.gp_obj.get_target_reached())
                    i += 1
                
                sleep(0.01)
                
        self.teardown()  # stop
        
        print 'ploting'
#         max_index, max_value = max(enumerate(actual_velocity_list), key=operator.itemgetter(1))
#         min_index, min_value = min(enumerate(actual_velocity_list), key=operator.itemgetter(1))
#         print 'max_speed: ', max_value, 'in second: ', time_list[max_index]
        '''ploting'''
        fig = plt.figure(1)
        i = 0
        for node in self.gp_nodes_list:
            plt.plot(result_list[i][TIME_INDX], result_list[i][VEL_INDX], 'o', label="actual velocity node %d"%node.node_id)
            plt.plot(result_list[i][TIME_INDX], result_list[i][TARGET_INDX], linestyle='--', label="target reported by motor node %d"%node.node_id)
            plt.plot(result_list[i][TIME_INDX], result_list[i][TARGET_REACH_INDX], label="target reached node %d"%node.node_id)
            i += 1
        
        
        fig.suptitle('actual_velocity_list', fontsize=12, fontweight='bold')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
        plt.ylabel('velocity [RPM]')
        plt.xlabel('time [s]')
        plt.grid(True)
        plt.show()

    def test_accuracy_motor(self):
        self.test_speed_targets([20, 25], step_time=5, offset=0.5)
        
    def test_high_speed_motor(self):
        self.test_speed_targets(targets_list=[10, 30, 60, 20, 45, 60, 5, 30], step_time=5)
        
    def test_low_speed_motor(self):
        self.test_speed_targets(targets_list=[3, 10, 5, 14, 5, 18, 5, 0, 5], step_time=10)
        
    
if __name__ == '__main__':
    can_h = can_handler.can_handler()
    can_h.configure('CANOpen')

    test_obj = test(can_h, num_nodes=2)
  
    '''test to execute: configure'''
    test_obj.setup()    
    
#     test_obj.test_vel_2()
    test_obj.test_accuracy_motor()
        
    '''teardown'''
    test_obj.teardown()
    print '**** END PROGRAM ****'
