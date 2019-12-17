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
import time
import sys
import threading
from yaml import load, Loader
import atexit
import chaturcar
import imageproc

import sys
import evdev
import joysticks

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

class XBoxThread(threading.Thread):
#XBox Thread
    def __init__(self, driver,joystick,params):
        threading.Thread.__init__(self)
        self.driver = driver
        self.joystick = joystick
        self.steer_speed, self.drive_speed = driver.get_commands()
        self.steer_step = params['steer_step']
        self.drive_step = params['drive_step']
        self.max_steer =  params['max_steer']
        self.max_drive =params['max_drive']

    def run(self):

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
                            change = -scale(event.value,(0,65535),(-self.max_drive,self.max_drive)) - self.drive_speed
                            if abs(change)>self.drive_step:
                                self.drive_speed = clamp(self.drive_speed + change,-self.max_drive,self.max_drive)
                                changed = True
                            #print('drive_speed: ',drive_speed)
                            #peculiarity in the way XBox controller works, inverting Y axis
                        if event.code == 2:         #X axis on right stick
                            #print(event.value)
                            #steer_speed = scale(event.value,(0,255),(-max_steer,max_steer))
                            change = scale(event.value,(0,65535),(-self.max_steer,self.max_steer))-self.steer_speed
                            if abs(change)>self.steer_step:
                                self.steer_speed = clamp(self.steer_speed + change,-self.max_steer,self.max_steer)
                                changed = True
                            #print('steer_speed: ',steer_speed)
                    if event.type == 1  and event.value == 1 and event.code in [310, 311,307]:
                        #print("X button is pressed. Stopping.")
                        self.driver.stop()
                        self.steer_speed = 0.0
                        self.drive_speed = 0.0

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


                    if event.type == 1  and event.value == 1 and event.code == 307:
                            print("X button is pressed. Exiting.")
                            self.driver.stop()
                            break
                    #print(steer_speed,drive_speed)
                    '''
                    if changed:
                        #print('sending')
                        self.driver.send_commands([self.steer_speed,self.drive_speed])

                except:
                    pass
                    #print('Problem Key Pressed')





    def shutdown(self):
        pass




def main():
    params = load(open('ChaturCar.yaml').read(), Loader=Loader)
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
    parser.add_argument('--modelpath', default=params['modelpath'])
    parser.add_argument('--modelfile', default=params['modelfile'])
    parser.add_argument('--model', default=params['model'])
    args = parser.parse_args()

    # Cleanup done at exit
    @atexit.register
    def shutdownChaturCar():
        print('EXITING')
        car.stop()
        #car.cleanup()
        pass

    #threads = list()
    #create collector, car and driver object
    if args.selfdrive == 'True' or args.collectdata == 'True':
        collector = imageproc.ImageProc(args,params)
        print('set up ImageProc')
    car = chaturcar.PiconCar()
    print('initiated Car')
    driver = chaturcar.ChaturDriver(car,args)
    print('initiated Driver')


    #create joystick object and start xbox thread
    if args.collectdata =='True' or args.Testing =='True':
        joystick = joysticks.XBoxJoyStick().joystick
        if not joystick:
            sys.exit('No JoyStick Found: Aborting')
        xbox_read = XBoxThread(driver,joystick,params)
        xbox_read.daemon = True
        xbox_read.start()
        #threads.append(xbox_read)

    '''
    Now threads as required
    Self Drive will be daemon like xbox thread
    for collecting example data and self driving
    '''
    #collect data
    if args.collectdata == 'True':
        #start moving the car forward for 2 seconds before starting data capture
        driver.forward()
        time.sleep(2)

        collect_data = threading.Thread(target=collector.collect_data,\
            args=(driver.get_category,driver.get_commands,),daemon=False)
        collect_data.start()
        print('Now Collecting Data')
        #threads.append(collect_data)

    #self drive
    if args.selfdrive == 'True':
        capture_image = threading.Thread(target=collector.capture_image,\
            args=(driver.get_category,driver.get_commands,),daemon=True)
        capture_image.start()
        threads.append(capture_image)
        self_drive = threading.Thread(target=driver.self_drive,args=(collector,))
        self_drive.start()
        print('Now Self Driving')
        #threads.append(self_drive)

      #join all threads
#      for index, thread in enumerate(threads):
#          thread.join()

    pass

if __name__=="__main__":
        main()
