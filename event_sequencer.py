#!usr/bin/env/ python
import RPi.GPIO as GPIO
import time, sched


def enable():
	GPIO.output(23, GPIO.HIGH)
	print "enable output", time.time()
def disable():
	GPIO.output(23, GPIO.DOWN)
	print "disable output", time.time()

#Configure
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#Event Queue
s = sched.scheduler(time.time, time.sleep)

s.enter(5, 1, enable, ())
s.enter(2, 1, disable, ()

print "start time"
