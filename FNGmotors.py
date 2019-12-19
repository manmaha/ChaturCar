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
      self.standby(level=False)
      pass


def main():
      parser = argparse.ArgumentParser(description='Motor Driver for RoboKar')
      parser.add_argument('--motor', default='both')
      parser.add_argument('--gain', default=50)
      parser.add_argument('--time', default=10)
      args = parser.parse_args()

      # Cleanup done at exit
      @atexit.register
      def cleanup_motors():
          print('EXITING')
          for m in (m1,m2): m.cleanup()
          pi.stop()
          pass

      params = load(open('MotorParams.yaml').read(), Loader=Loader)
      motorpins1 = params['motor1']
      motorpins2 = params['motor2']
      pi = pigpio.pi()
      pwm_freq = params['PWM_FREQ']
      max_dc = params['MAX_DC']
      m1 = motor(motorpins1,pi,pwm_freq,max_dc)
      m2 = motor(motorpins2,pi,pwm_freq,max_dc)

      if args.motor == 'both':
          for m in (m1,m2):m.forward(float(args.gain))
      else:
          if args.motor == '1':
              m1.forward(float(args.gain))
          else:
              m2.forward(float(args.gain))

      time.sleep(float(args.time))
      for m in (m1,m2): m.cleanup()
      pi.stop()

if __name__ == "__main__":
    main()
