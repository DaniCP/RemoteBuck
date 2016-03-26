#!usr/bin/env/ python
import RPi.GPIO as GPIO
import time


def enable():
	GPIO.output(23, GPIO.HIGH)
	print "enable output", time.time()
def disable():
	GPIO.output(23, GPIO.LOW)
	print "disable output", time.time()

def next_state:
	i = i+1
	if i>len(list(state_list)):
		return break
	else:
		state = state_list[i][0]
	        timeout = state_list[i][1]

#Configure
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.LOW)
GPIO.output(25, GPIO.LOW)


#State machine
state_list = [(0,3), (1,5), (2,8)]

state = 0
timeout = 0
i=0

start_time = time.time()
print "start time: ", start_time

while True:
	time.sleep(1)
	if (state ==0):
		next_state()
	if ((state == 1) & (time.time()-start_time>timeout)):
		enable()
		start_time = time.time()
	if ((state == 2) & (time.time()-start_time>timeout)):
		disable()
		start_time = time.time()

