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
        self.max_steer =  params['max_steer']
        self.max_drive =params['max_drive']

    def run(self):
        if self.joystick:
            for event in self.joystick.read_loop():
                steer_speed,drive_speed = self.driver.get_commands()
                changed = False
                if event.type == 3:
                    if event.code == 1:         #Y axis on left stick
                        #peculiarity in the way XBox controller works, inverting Y axis
                        drive_speed = -scale(event.value,(0,65535),\
                                        (-self.max_drive,self.max_drive))
                        changed = True
                    if event.code == 2:         #X axis on right stick
                        steer_speed = scale(event.value,(0,65535),\
                               (-self.max_steer,self.max_steer))
                        changed = True
                if event.type == 1  and event.value == 1 and event.code in [308,309]:
                    self.driver.stop()
                if event.type == 1  and event.value == 1 and event.code == 307:
                    self.driver.stop_driving()
                    print("Exiting")
                    break
                if event.type == 1  and event.value == 1 and event.code == 306:
                    self.driver.pause()
                    print("Pausing")
                if event.type == 1  and event.value == 1 and event.code == 304:
                    self.driver.start_after_pause()
                if changed:
                    #print('sending', steer_speed,drive_speed)
                    self.driver.send_commands([steer_speed,drive_speed])

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
    parser.add_argument('--example', default=params['example'])
    parser.add_argument('--framerate',default=params['framerate'])
    parser.add_argument('--max_steer',default=params['max_steer'])
    parser.add_argument('--max_drive',default=params['max_drive'])
    parser.add_argument('--labels', default=params['labels'])
    parser.add_argument('--modelpath', default=params['modelpath'])
    parser.add_argument('--modelfile', default=params['modelfile'])
    parser.add_argument('--model', default=params['model'])
    parser.add_argument('--category_names',default=params['category_names'])
    parser.add_argument('--steer_speeds',default=params['steer_speeds'])
    args = parser.parse_args()

    # Cleanup done at exit
    @atexit.register
    def shutdownChaturCar():
        try:
            car.stop()
            print('Stopped before Exit')
            car.cleanup()
            print('Cleaned Up')
        except:
            pass

    threads = list()
    #create collector, car and driver object
    car = chaturcar.FNGCar()
    driver = chaturcar.ChaturDriver(car,args)
    #create joystick object and start xbox thread
    if args.collectdata =='True' or args.testing =='True'or args.selfdrive == 'True':
        joystick = joysticks.JoyStick('Xbox Wireless Controller').joystick
        if not joystick:
            car.stop()
            car.cleanup()
            sys.exit('No JoyStick Found: Aborting')
        xbox_read = XBoxThread(driver,joystick,params)
        xbox_read.daemon = True
        xbox_read.start()
        threads.append(xbox_read)
    if args.selfdrive == 'True' or args.collectdata == 'True':
        collector = imageproc.ImageProc(args,params)
    '''
    Now threads as required
    '''
    #collect data
    if args.collectdata == 'True':
        collect_data = threading.Thread(target=collector.collect_data,\
            args=(driver.get_category,driver.get_commands,driver.is_driving,\
            driver.is_paused,),daemon=False)
        collect_data.start()
        print('Starting Collect Data Module')
        threads.append(collect_data)

    #self drive
    if args.selfdrive == 'True':
        capture_image = threading.Thread(target=collector.capture_image,\
            args=(driver.get_category,driver.get_commands,\
             driver.is_driving,driver.is_paused,),daemon=False)
        capture_image.start()
        print('Starting Image Capture Module')
        threads.append(capture_image)
        self_drive = threading.Thread(target=driver.self_driver,\
                args=(collector,driver.is_driving,driver.is_paused,),daemon=False)
        self_drive.start()
        print('Starting Self Driving Module')
        threads.append(self_drive)

      #join all threads
    #for index, thread in enumerate(threads):
    #    thread.join()

    pass

if __name__=="__main__":
        main()
