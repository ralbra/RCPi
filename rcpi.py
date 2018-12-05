#Script to control servos with a joystick on an raspberry pi
#@author: ralbra
#@license: GPLV3 

from time import sleep
import pygame
import sys
import pigpio
import threading

j = 0

def connectJoystick():
	print 'Waiting for joystick... (press CTRL+C to abort)'
	while True:
		try:
			try:
				pygame.joystick.init()
				# Attempt to setup the joystick
				if pygame.joystick.get_count() < 1:
					# No joystick attached, set LEDs blue
					pygame.joystick.quit()
					sleep(0.5)
				else:
					# We have a joystick, attempt to initialise it!
					global j
					j = pygame.joystick.Joystick(0)
					break
			except pygame.error:
				# Failed to connect to the joystick, set LEDs blue
				pygame.joystick.quit()
				sleep(0.5)
		except KeyboardInterrupt:
			# CTRL+C exit, give up
			print 'User aborted'
			sys.exit()
	print 'Joystick found'
	j.init()

pygame.init()
connectJoystick()

print bool(j.get_init())
print int(j.get_id())
print int(j.get_numaxes())
print int(j.get_numbuttons())

pi = pigpio.pi()

steer_pin = 14
accel_pin = 18
MIN_WIDTH= 500
MAX_WIDTH= 2500
MID_STEER= 1500
MID_ACCEL= 1500
minAccel = 0
maxAccel = 0
minSteer = 0
maxSteer = 0
running = True
ACCEL_BACKWARD_BUTTON = 8
ACCEL_BACKWARD_AXIS = 12
ACCEL_FORWARD_BUTTON = 9
ACCEL_FORWARD_AXIS = 13
BUTTON_REVERSE_STEER = 0
BUTTON_REVERSE_ACCEL = 3
BUTTON_TRIM_STEER_LEFT = 7
BUTTON_TRIM_STEER_RIGHT = 5
BUTTON_TRIM_FORWARD = 6
BUTTON_TRIM_BACKWARD = 4
BUTTON_LIMIT_ACCEL = 14

STEER_REVERSE = 1
counter = 10000

#TODO check every 10 seconds if the controller is connected
def checkJoystick():
	pygame.joystick.quit()
	pygame.joystick.init()
	if pygame.joystick.get_count() < 1:
		print "controller disconnected"
		connectJoystick
		
def drive():
	global MID_STEER
	global MID_ACCEL
	global minAccel
	global maxAccel
	global minSteer
	global maxSteer
	global counter
	global ACCEL_BACKWARD_BUTTON
	global ACCEL_BACKWARD_AXIS
	global ACCEL_FORWARD_BUTTON
	global ACCEL_FORWARD_AXIS 
	global BUTTON_REVERSE_STEER
	global BUTTON_REVERSE_ACCEL
	global BUTTON_TRIM_STEER_LEFT
	global BUTTON_TRIM_STEER_RIGHT
	global BUTTON_TRIM_FORWARD
	global BUTTON_TRIM_BACKWARD
	global STEER_REVERSE
	global BUTTON_LIMIT_ACCEL
	try:
	  while running:
		pygame.event.pump()
		#just in case no proper input
		accel_axis= 0
		steer_axis= 0
		steer= MID_STEER
		accel= MID_ACCEL
		
		#check for controller presence	
		# counter -= 1
		# if counter <= 0:
			# print("check for controller")
			# checkJoystick()
			# counter = 10000
		
		#trimming
		#left
		if j.get_button(BUTTON_TRIM_STEER_LEFT):
			MID_STEER = MID_STEER - 5
			sleep(0.1)
		#right
		if j.get_button(BUTTON_TRIM_STEER_RIGHT):
			MID_STEER = MID_STEER + 5
			sleep(0.1)
		#up
		if j.get_button(BUTTON_TRIM_FORWARD):
			MID_ACCEL = MID_ACCEL - 5
			sleep(0.1)
		#down
		if j.get_button(BUTTON_TRIM_BACKWARD):
			MID_ACCEL = MID_ACCEL + 5
			sleep(0.1)
		#recalculate max and min
		minAccel = (MID_ACCEL - MIN_WIDTH) / 2
		maxAccel = (MAX_WIDTH - MID_ACCEL) / 2
		minSteer = (MID_STEER - MIN_WIDTH)
		maxSteer = (MAX_WIDTH - MID_STEER)
		
		#reverse accel
		if j.get_button(BUTTON_REVERSE_ACCEL):
			temp = ACCEL_BACKWARD_BUTTON 
			ACCEL_BACKWARD_BUTTON = ACCEL_FORWARD_BUTTON
			ACCEL_FORWARD_BUTTON= temp
			temp = ACCEL_BACKWARD_AXIS
			ACCEL_BACKWARD_AXIS = ACCEL_FORWARD_AXIS
			ACCEL_FORWARD_AXIS = temp
			sleep(1)
		
		#for more precise acceleration press X button
		if j.get_button(BUTTON_LIMIT_ACCEL):
			minAccel = 	minAccel / 2
			maxAccel = 	maxAccel / 2
		#get accel
		if j.get_button(ACCEL_BACKWARD_BUTTON):
			accel_axis= j.get_axis(ACCEL_BACKWARD_AXIS) +1
			accel= MID_ACCEL - accel_axis * minAccel
		elif j.get_button(ACCEL_FORWARD_BUTTON):
			accel_axis= j.get_axis(ACCEL_FORWARD_AXIS) + 1
			accel= MID_ACCEL + accel_axis * maxAccel
		
		
		#reverse steering
		if j.get_button(BUTTON_REVERSE_STEER):
			STEER_REVERSE = STEER_REVERSE * -1
			sleep(1)
		
		#get steering
		steer_axis = j.get_axis(0) * STEER_REVERSE
		if steer_axis < 0:
			steer= MID_STEER + steer_axis * minSteer
		elif steer_axis > 0:
			steer= MID_STEER + steer_axis * maxSteer
		
		pi.set_servo_pulsewidth(steer_pin, steer)
		pi.set_servo_pulsewidth(accel_pin, accel)
		
		sleep(0.001)
	#TODO try to reconnect after controller got out of range
	except pygame.error:
		print('pygame error')
		
	except KeyboardInterrupt:
		j.quit()
		pi.set_servo_pulsewidth(steer_pin, 0)
		pi.set_servo_pulsewidth(accel_pin, 0)
		pi.stop()
		pygame.quit
		sys.exit()

drive()
sys.exit()