#!/usr/bin/env python3
'''	Bluetooth Joystick driver
	Defines joystick Object Class
	For PS3 and XBox

	MM 9 Dec 2019
'''

import evdev
class JoyStick(object):
	def __init__(self,jstickName):
		print('Finding ', jstickName)
		self.joystick = None
		devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		for device in devices:
		#print(device.name)
			if device.name == jstickName:
				self.device = device
				self.joystick = evdev.InputDevice(device.fn)
				print(device.name, 'found')
				break
		if not self.joystick:
			print('No  Joystick Found')

	def capabilities(self,verbose=True):
		return self.device.capabilities(verbose=verbose)

'''
class XBoxJoyStick(JoyStick):
	def __init__(self):
		super(JoyStick,self).__init__('Xbox Wireless Controller')

class PS3JoyStick(JoyStick):
	def __init__(self):
		super(JoyStick,self).__init__('PLAYSTATION(R)3 Controller')
'''
