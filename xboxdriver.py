#!/usr/bin/env python3
''' ChaturCar - Clever Car Class
Self Driving Car based on Picon Zero, Camera, Edge TPU and RC Car Chassis
Car has a steering motor and a driving motor

Steering and Drive Commands for Training are received through a PS3 Driver
Manish Mahajan
19 November 2019
'''

import argparse
import signal
import sys
import threading
from yaml import load, Loader
import atexit
import chaturcar
import imageproc
import models
import sys
import evdev
import joystick

## Some helpers ##
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.

    val: float or int
    src: tuple
    dst: tuple

    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(0,255),(-100,100))

def clamp(value, floor=-100, ceil=100):
    """
    Clamp the value within the floor and ceiling values.
    """
    return max(min(value, ceil), floor)

class PS3Thread(threading.Thread):
#PS3 Thread
    def __init__(self, driver,joystick):
        threading.Thread.__init__(self)
        self.driver = driver
        self.joystick = joystick

    def run(self):
        steer_speed = 0.0
        drive_speed = 0.0
        steer_step = 0.5
        drive_step = 0.15
        max_steer =  1.0
        max_drive = 0.45
        #print(self.joystick)
        if self.joystick:
            for event in self.joystick.read_loop():
                changed = False
                try:
                    #One of the sticks is moved
                    keyevent = evdev.categorize(event)
                    if event.type == 3:
                        if event.code == 1:         #Y axis on left stick
                            #print(event.value)
                            change = -scale(event.value,(0,65535),(-max_drive,max_drive)) - drive_speed
                            if abs(change)>drive_step:
                                drive_speed = clamp(drive_speed + change,-max_drive,max_drive)
                                changed = True
                            #print('drive_speed: ',drive_speed)
                            #peculiarity in the way XBox controller works, inverting Y axis
                        if event.code == 2:         #X axis on right stick
                            #print(event.value)
                            #steer_speed = scale(event.value,(0,255),(-max_steer,max_steer))
                            change = scale(event.value,(0,65535),(-max_steer,max_steer))-steer_speed
                            if abs(change)>steer_step:
                                steer_speed = clamp(steer_speed + change,-max_steer,max_steer)
                                changed = True
                            #print('steer_speed: ',steer_speed)
                    if event.type == 1  and event.value == 1 and event.code in [310, 311]:
                        #print("X button is pressed. Stopping.")
                        self.driver.stop()
                        steer_speed = 0.0
                        drive_speed = 0.0

                        '''
                        if "BTN_DPAD_UP" in keyevent.keycode:
                            drive_speed =min(max_drive, drive_speed+drive_step)
                            changed = True
                        elif "BTN_DPAD_DOWN" in keyevent.keycode:
                            drive_speed =max(-max_drive, drive_speed-drive_step)
                            changed = True
                        elif "BTN_DPAD_RIGHT" in keyevent.keycode:
                            steer_speed =min(max_steer, steer_speed+steer_step)
                            changed = True
                        elif "BTN_DPAD_LEFT" in keyevent.keycode:
                            steer_speed= max(-max_steer, steer_speed-steer_step)
                            changed = True

                        '''
                    if event.type == 1  and event.value == 1 and event.code == 307:
                            print("X button is pressed. Exiting.")
                            self.driver.stop()
                            break
                    #print(steer_speed,drive_speed)
                    if changed:
                        #print('sending')
                        self.driver.send_commands([steer_speed,drive_speed])

                except:
                    pass
                    #print('Problem Key Pressed')





    def shutdown(self):
        pass




def main():
    params = load(open('driver.yaml').read(), Loader=Loader)
    parser = argparse.ArgumentParser(description='Driver for ChaturCar')
    parser.add_argument('--hostname', default=params['hostname'])
    parser.add_argument('--port', default=params['port'])
    parser.add_argument('--testing',default=params['testing'])
    parser.add_argument('--selfdrive',default=params['selfdrive'])
    parser.add_argument('--collectdata',default=params['collectdata'])
    parser.add_argument('--record_time',default=params['record_time'])
    parser.add_argument('--drive_time',default=params['drive_time'])
    parser.add_argument('--example', default=params['example'])
    parser.add_argument('--framerate',default=params['framerate'])
    parser.add_argument('--avg_drive',default=params['avg_drive'])
    parser.add_argument('--avg_steer',default=params['avg_steer'])
    parser.add_argument('--labels', default=params['labels'])

    args = parser.parse_args()

    # Cleanup done at exit
    @atexit.register
    def shutdownChaturCar():
        print('EXITING')
        car.stop()
        #car.cleanup()
        pass

    car = chaturcar.ChaturCar()
    driver = chaturcar.ChaturDriver(car,args)
    #car.test()
    if args.selfdrive == 'True' or args.collectdata == 'True':
        collector = imageproc.ImageProc(args)
    joystick = joystick.XBoxJoyStick().joystick
    if joystick : #joystick found
      #start the threaded processes
      threads = list()
      '''
      Thread to receive commands goes here
      '''
      #start the PS3 Driver for reading commands - this is the main thread

      ps3_read = PS3Thread(driver,joystick)
      ps3_read.daemon = True
      ps3_read.start()
      threads.append(ps3_read)

      '''
      Now the daemon threads as required
      for collecting example data and self driving
      '''
      #collect data
      if args.collectdata == 'True':
        collect_data = threading.Thread(target=collector.collect_data, args=(driver.get_class,),daemon=False)
        collect_data.start()
        threads.append(collect_data)
      #self drive
      if args.selfdrive == 'True':
        capture_image = threading.Thread(target=collector.capture_image,daemon=True)
        capture_image.start()
        threads.append(capture_image)
        self_drive = threading.Thread(target=driver.self_drive,args=(collector,),daemon=True)
        self_drive.start()
        threads.append(self_drive)

      #join all threads
#      for index, thread in enumerate(threads):
#          thread.join()

    pass

if __name__=="__main__":
        main()
