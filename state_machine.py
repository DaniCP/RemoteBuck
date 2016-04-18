#!usr/bin/env/ python
# import RPi.GPIO as GPIO
import time


class StateMachine:
	def __init__(self):
		self.state_list = [(0,3), (1,5), (2,8)]
		self.end = 0
		self.state = 0
		self.timeout = 0
		self.i = 0

	def state_enable(self):
	#GPIO.output(23, GPIO.HIGH)
		print "state_enable output", time.time()
	
	def state_disable(self):
	# 	GPIO.output(23, GPIO.LOW)
		print "state_disable output", time.time()
	
	def next_state(self):
		if self.i>=len(list(self.state_list)):
			self.end = 1
		else:			
			self.state = self.state_list[self.i][0]
			self.timeout = self.state_list[self.i][1]
			print'Change state: ', self.state, ' timeout: ', self.timeout, ' actual time: ', time.time()
		self.i = self.i+1
	
	def configure(self):
		pass
	# GPIO.setmode(GPIO.BCM)
	# GPIO.setup(23, GPIO.OUT)
	# GPIO.setup(24, GPIO.OUT)
	# GPIO.setup(25, GPIO.OUT)
	# GPIO.output(23, GPIO.LOW)
	# GPIO.output(24, GPIO.LOW)
	# GPIO.output(25, GPIO.LOW)

	def run(self):
		#State machine
		start_time = time.time()
		print "start time: ", start_time
		m.next_state()
		while not self.end:
			time.sleep(1)
			if ((self.state == 0) & (time.time()-start_time>self.timeout)):
				start_time = time.time()
				self.next_state()
				
			if (self.state == 1):
				#actions
				self.state_enable()
				if (time.time()-start_time>self.timeout):					
					#exit transition
					start_time = time.time()
					self.next_state()
					
			if (self.state == 2):
				self.state_disable()
				if (time.time()-start_time>self.timeout):				
					start_time = time.time()
					self.next_state()
# 			print 'main-> state: ', self.state, ' timeout: ', self.timeout


if __name__== "__main__":
	m = StateMachine()
	#State machine
	m.run()
	print '**** END PROGRAM ****'

