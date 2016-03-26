#!usr/bin/env/ python
import argparse
import RPi.GPIO as GPIO

parser = argparse.ArgumentParser()

parser.add_argument("-g", "--gpio", type=int, default=0,
                    help="GPIO used")
parser.add_argument("-a", "--action", type=str, default='disable',
                    help="enable or disable")

args = parser.parse_args()

gpio_num = args.gpio
print 'a is: ', args.action


if args.action == 'enable':
# #enciende
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_num, GPIO.OUT)
    GPIO.output(gpio_num, GPIO.HIGH)

if args.action == 'disable':
# ## apaga.py
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_num, GPIO.OUT)
    GPIO.output(gpio_num, GPIO.LOW)
    GPIO.cleanup()

