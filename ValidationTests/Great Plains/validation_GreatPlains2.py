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
        
    def _test_target_reached(self):
        '''check target reached when +-2 rpm'''
        speed_target = 60
        self.gp_obj.set_speed(speed_target)
        time_start = time.time()
        timeout = 10 # seconds
        while (not self.gp_obj.get_target_reached()=='1' or time.time()-time_start>timeout):
            sleep(0.050)
         
        actual_speed = self.gp_obj.get_actual_speed()
        time_spent = time.time() - time_start
         
        assert abs(speed_target - actual_speed) < 2, "Target reached FAIL"
        
    def _test_stop_when_speed0(self):
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

    def _test_aceleration(self):
        '''to check the acceleration parameter is functional
        only time variation checked
        We can not ensure that the motor is reaching the desired acceleration'''
        last_speed = 0
        list = []
        self.gp_obj.set_speed(30)           
        time_start = time.time()
        speed = self.gp_obj.get_actual_speed()
        while ((speed+last_speed)/2<28 or speed==0):            
            last_speed = speed
            sleep(0.1)
            speed = self.gp_obj.get_actual_speed()
            list.append((time.time()-time_start,speed))
#             print "speed: ",speed, "last_speed: ", last_speed
        time_spent = time.time() - time_start
        print list
        assert time_spent < 1.5, "aceleration fail"

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
        
    def test_position_accuracy(self):
        target_list = [1,2,3,4,5]
        result_list = []
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
