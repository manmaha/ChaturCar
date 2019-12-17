#!/usr/bin/env python3
'''
Motor Driver Routines
Using pigpio library
Manish Mahajan
29 Sep 2019
TB6612FNG Motor Driver
pigpio has to be running as a daemon
sudo pigpiod
'''
import pigpio
import time
import argparse
import atexit
from yaml import load, Loader

# Motor is an object, setup defined as list of gpiopins and motor_type (A or B)
# TB6612FNG Motor Driver controls two motors, Motor A and Motor B
# Will use Hardware PWM

class Motor(object):
  def __init__(self,gpiopins,pi,pwm_freq=800,max_dc=100):
    #Get Parameters
    # intitalise parameters
    #gpiopins is a list of pins in this order:
    #PWM,In1,In2, Stdby
    #StdBy has to be pulled to High for motor to be working
    #All pins have to designated as Output
    self.pi = pi
    self.PWM = gpiopins[0]
    self.In1 = gpiopins[1]
    self.In2 = gpiopins[2]
    self.stdby = gpiopins[3]
    self.max_dc = max_dc
    for pin in gpiopins[1:]:
        pi.set_mode(pin, pigpio.OUTPUT)
    pi.set_PWM_range(self.PWM,max_dc)
    pi.set_PWM_frequency(self.PWM,pwm_freq)
    self.standby()
    pass


  def standby(self, level = True):
  #puts the motor in stdby mode
    self.pi.write(self.stdby,level)
    pass

  def move(self, gain , direction = True): #True for forward, False for backwards
  #simple move command
    if direction :
        self.pi.write(self.In1,1)
        self.pi.write(self.In2,0)
    else:
        self.pi.write(self.In1,0)
        self.pi.write(self.In2,1)
    self.pi.set_PWM_dutycycle(self.PWM,min(gain,self.max_dc))
    pass

  def forward(self,gain):
  #moves the motor forward
    self.pi.write(self.In1,1)
    self.pi.write(self.In2,0)
    self.pi.set_PWM_dutycycle(self.PWM,min(gain,self.max_dc))
    pass

  def back(self,gain):
  # moves the motor backwards

    self.pi.write(self.In1,0)
    self.pi.write(self.In2,1)
    self.pi.set_PWM_dutycycle(self.PWM,min(gain,self.max_dc))
    pass

  def brake(self):
  # brakes the motor
    self.pi.write(self.In1,1)
    self.pi.write(self.In2,1)
    self.pi.set_PWM_dutycycle(self.PWM,0)
    pass

  def stop(self):
  # stops the motor
    self.pi.write(self.In1,0)
    self.pi.write(self.In2,0)
    self.pi.set_PWM_dutycycle(self.PWM,0)
    pass

  def cleanup(self):
      self.pi.standby(level=False)
      pass


'''
Object with two Motors - can be diff drive or steer drive
'''

class Car(object):
    def __init__(self):
      params = load(open('MotorParams.yaml').read(), Loader=Loader)
      motorpins = params['motorpins']
      pwm_freq = params['PWM_FREQ']
      max_dc = params['MAX_DC']
      pi = pigpio.pi()
      self.motors = [motor(gpiopins,pi,pwm_freq,max_dc) for gpiopins in motorpins]
      self.speed = [0.0,0.0]
      self.stop()
      pass

    def drive(self,commands):
        self.speed = commands
        self.motors[0].move(commands[0])
        self.motors[1].move(commands[1])
        pass

    def get_speed(self):
        return self.speed

    def drive(self,commands):
        #implemented specific to each car subclass
        pass

    def stop(self):
        for m in self.motors:
            m.stop()
        pass

    def test(self):
        print('Testing Car')
        print('Forward 1 seconds')
        self.forward(25)
        time.sleep(1)
        self.stop()
        print('Backward 1 seconds')
        self.reverse(25)
        time.sleep(1)
        self.stop()
        print('Test Steering')
        self.steer_left()
        time.sleep(1)
        self.steer_right()
        time.sleep(1)
        self.stop()
        print('Test Circle')
        self.drive([50,50])
        time.sleep(1)
        self.stop()
        self.drive([-50,-50])
        time.sleep(1)
        self.stop()


    def cleanup(self):
        for m in self.motors:
            m.cleanup()

class SteerDriveCar(Car):
    ''' Steer Drive Car, Motor A = Steer, Motor B = Drive
    '''
    def __init__(self):
        super(SteerDriveCar,self).__init__(pi)
        pass

    def drive(self,commands):
        super(SteerDriveCar,self).drive(commands)
        # this is specific to this chassis set up
        #steer_speed = commands[0]
        #drive_speed = commands[1]
        pass

    def forward(self,speed=100):
        self.drive([0,speed])
    def reverse(self,speed=100):
        self.drive([0,-speed])
    def steer_left(self,speed=100):
        self.drive([-speed,0])
    def steer_right(self,speed=100):
        self.drive([speed,0])




def main():
    print('Testing Diff Drive Model')
    car = cars.DiffDriveCar()
    car.test()
    car.cleanup()
