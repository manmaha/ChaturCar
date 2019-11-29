#!/usr/bin/env python3
'''	PS3 Joystick driver
	Defines joystick Object Class

	MM 29 Nov 2019
'''

import evdev

class PS3JoyStick(object):
	def __init__(self):
		print ('Finding PS3 Controller')
		self.joystick = None
		devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		for device in devices:
		#print(device.name)
			if device.name == 'PLAYSTATION(R)3 Controller':
				self.joystick = evdev.InputDevice(device.fn)
				print(device.name, 'found')
				break
		if not self.joystick:
			print('No  Joystick Found')

