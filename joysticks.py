#!/usr/bin/env python3
'''	Bluetooth Joystick driver
	Defines joystick Object Class
	For PS3 and XBox

	MM 9 Dec 2019
'''

import evdev

class XBoxJoyStick(object):
	def __init__(self):
		print ('Finding XBox Controller')
		self.joystick = None
		devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		for device in devices:
		#print(device.name)
			if device.name == 'Xbox Wireless Controller':
				self.joystick = evdev.InputDevice(device.fn)
				print(device.name, 'found')
				break
		if not self.joystick:
			print('No  Joystick Found')

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
