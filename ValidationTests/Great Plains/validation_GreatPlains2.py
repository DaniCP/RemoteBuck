# -*- coding: utf-8 -*-
import unittest
import sys, os
from time import sleep
import time
from bitstring import BitString, BitArray

sys.path.append(os.getcwd() + '\..\..\CAN')
import can_handler
from validation_GreatPlains import greate_plains

class VelocityControlTestCase(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        print "velocity control setup"
        self.can_h = can_handler.can_handler()
        self.can_h.configure('CANOpen')
        self.gp_obj = greate_plains(self.can_h, 0x601)
        
        self.gp_obj.set_operational()
        self.gp_obj.set_heartbeat(1500)        
        self.gp_obj.heartbeat_start()
        self.gp_obj.clear_errors()
        self.gp_obj.set_mode(2)

    def tearDown(self):
        """Call after every test case."""        
        self.gp_obj.set_speed(0)
        self.gp_obj.heartbeat_stop()
        
    def test_target_reached(self):
        '''check target reached when +-2 rpm'''
        speed_target = 30
        self.gp_obj.set_speed(speed_target)
        time_start = time.time()
        timeout = 10 # seconds
        while (not self.gp_obj.get_target_reached()=='1' and time.time()-time_start<timeout):
            sleep(0.050)
         
        actual_speed = self.gp_obj.get_actual_speed()
        time_spent = time.time() - time_start
         
        assert abs(speed_target - actual_speed) < 2, "Target reached FAIL"
        
    def test_stop_when_speed0(self):
        speeds = [25, 40, 60]
        for i in range(0,3):
            self.gp_obj.set_speed(speeds[i])
            sleep(3)
            assert self.gp_obj.get_actual_speed() > 0, "problem starting the test"
            self.gp_obj.set_speed(0)
            sleep(3)
            t_end = time.time() + 6
            while time.time() < t_end:
                sleep(0.5)
                actual_speed = self.gp_obj.get_actual_speed()
                assert actual_speed == 0, "motor does not stop after set speed = 0"

    def test_acceleration(self):
        '''to check the acceleration parameter is functional
        only time variation checked
        We can not ensure that the motor is reaching the desired acceleration'''
        last_speed = 0
        list = []
        self.gp_obj.set_speed(30)           
        time_start = time.time()
        speed = self.gp_obj.get_actual_speed()
        while ((speed+last_speed)/2<28 or speed==0):    #  moving average
            last_speed = speed
            sleep(0.1)
            speed = self.gp_obj.get_actual_speed()
            list.append((time.time()-time_start,speed))
#             print "speed: ",speed, "last_speed: ", last_speed
        time_spent = time.time() - time_start
#         print list
        print 'non aplicable test' 
        assert time_spent < 1.5, "acceleration fail"

class PositionControlTestCase(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self.can_h = can_handler.can_handler()
        self.can_h.configure('CANOpen')
        self.gp_obj = greate_plains(self.can_h, 0x601)
        
        self.gp_obj.set_operational()
        self.gp_obj.set_heartbeat(1500)        
        self.gp_obj.heartbeat_start()
        self.gp_obj.clear_errors()
        self.gp_obj.set_mode(1)
        self.gp_obj.set_speed(60)

    def tearDown(self):
        """Call after every test case."""        
        self.gp_obj.set_speed(0)
        self.gp_obj.heartbeat_stop()
        
    def test_move_to_pos_using_velocity_command(self):
        speed_list = [60, 30, 10]
        tol_per = 15    #    tolerance percentage
        in_progress_speed_list = []
        pos_target = 5
        for i in speed_list:            
            self.gp_obj.set_speed(i)
            self.gp_obj.set_pos_target(pos_target)
            time_start = time.time()
            while (not self.gp_obj.get_target_reached()=='1'):
                sleep(0.100)
            time_spent = time.time() - time_start
            rpm = pos_target * 60 /time_spent
            print "real rpms: ", rpm
            assert rpm < i+tol_per*i/100.0 and rpm > i-tol_per*i/100.0
            
    def test_target_higher_than_allowed(self):
        max_allowed = 5
        self.gp_obj.set_pos_target(8)
        while (not self.gp_obj.get_target_reached()=='1'):
                sleep(0.050)
        sleep(1)
        actual_pos = self.gp_obj.get_actual_position()
        assert actual_pos == max_allowed
    
    def test_process_new_speed_after_finish(self):                    
        pos_target = 5
        tol_per = 15    # percentage tolerance
        timeout = False
        self.gp_obj.set_speed(10)
        self.gp_obj.set_pos_target(pos_target)
        time_start = time.time()
        only_one_flag = False
        while ((not self.gp_obj.get_target_reached()=='1') and not timeout):
            sleep(0.100)
            if only_one_flag is False:
                self.gp_obj.set_speed(60)
                only_one_flag = True
                
            if (time.time()-time_start>40):
                timeout = True
                assert False, "target_reached never set, timeout while waiting for target reached"
        time_spent = time.time() - time_start
        rpm = pos_target * 60 /time_spent
        print "real rpms: ", rpm, ' time_spent: ', time_spent
        assert rpm < 10+tol_per*10/100.0 and rpm > 10-tol_per*10/100.0
        
#         self.gp_obj.set_pos_target(pos_target)
#         time_start = time.time()
#         while (not self.gp_obj.get_target_reached()=='1' and time.time()-time_start<10):
#             sleep(0.100)
#         time_spent = time.time() - time_start
#         rpm = pos_target * 60 /time_spent
#         print "real rpms: ", rpm
#         assert rpm < 60+tol_per*60/100.0 and rpm > 60-tol_per*60/100.0
        
    def test_process_new_pos_target_after_finish(self):
        pass
    
    def test_position_accuracy(self):
        ''' improvement: should be checked externally, internally always get error 0'''
        target_list = [1,2,3,4,5]
        result_list = []
#         self.gp_obj.set_speed(3)
        
        for i in target_list:
            self.gp_obj.set_pos_target(i)
            time_start = time.time()
            timeout = 10
            sleep(0.5)
            while (not self.gp_obj.get_target_reached()=='1' or time.time()-time_start>timeout):
                sleep(0.050)
            sleep(2)
            result_list.append(self.gp_obj.get_actual_position())
        print result_list
        assert result_list==target_list, "fail reaching the target"
         

if __name__ == '__main__':
#     unittest.main() # run all tests
    test_class = eval(sys.argv[1])
    suite = unittest.TestLoader().loadTestsFromTestCase(PositionControlTestCase)
    unittest.TextTestRunner().run(suite)
    print '**** END PROGRAM ****'
