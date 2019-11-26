#!/usr/bin/env python3
''' ChaturCar - Clever Car Class
Self Driving Car based on Picon Zero, Camera, Edge TPU and RC Car Chassis
Car has a steering motor and a driving motor

Steering and Drive Commands for Training are received through a keyboard UI
Manish Mahajan
25 September 2019
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
import tty
import termios

class KeyboardThread(threading.Thread):
#Keyboard Thread
    def __init__(self, driver):
        threading.Thread.__init__(self)
        self.driver = driver

    def readchar(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ch == '0x03':
            raise KeyboardInterrupt
        return ch

    def readkey(self,getchar_fn=None):
        getchar = getchar_fn or self.readchar
        c1 = getchar()
        if ord(c1) != 0x1b:
            return c1
        c2 = getchar()
        if ord(c2) != 0x5b:
            return c1
        c3 = getchar()
        return chr(0x10 + ord(c3) - 65)  # 16=Up, 17=Down, 18=Right, 19=Left arrows

    def run(self):
        steer_speed = 0.0
        drive_speed = 0.0
        steer_step = 0.5
        drive_step = 0.15
        max_steer =  1.0
        max_drive = 0.45
        try:
            while True:
                keyp = self.readkey()
                if keyp == 'w' or ord(keyp) == 16:
                    drive_speed =min(max_drive, drive_speed+drive_step)
                elif keyp == 'z' or ord(keyp) == 17:
                    drive_speed =max(-max_drive, drive_speed-drive_step)
                elif keyp == 's' or ord(keyp) == 18 or keyp == '.' or keyp == '>':
                    steer_speed =min(max_steer, steer_speed+steer_step)
                elif keyp == 'a' or ord(keyp) == 19 or keyp == ',' or keyp == '<':
                    steer_speed= max(-max_steer, steer_speed-steer_step)
                elif keyp == ' ':
                    self.driver.stop()
                    steer_speed = 0.0
                    drive_speed = 0.0
                elif ord(keyp) == 3:
                    break
                commands = [steer_speed,drive_speed]
                self.driver.send_commands(commands)

        except KeyboardInterrupt:
            print()

        finally:
            pass


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
    args = parser.parse_args()

    # Cleanup done at exit
    @atexit.register
    def shutdownChaturCar():
        print('EXITING')
        car.stop()
        #car.cleanup()
        #server.shutdown()
        pass

    car = chaturcar.ChaturCar()
    driver = chaturcar.ChaturDriver(car,args)
    #car.test()
    if args.selfdrive == 'True' or args.collectdata == 'True':
        collector = ImageProc(args)

    #start the threaded processes
    threads = list()
    '''
    Thread to receive commands goes here
    '''
    #start the keyboard server for reading commands - this is the main thread
    keyboard_read = KeyboardThread(driver)
    keyboard_read.start()
    threads.append(keyboard_read)

    '''
    Now the daemon threads as required
    for collecting example data and self driving
    '''
    #collect data
    if args.collectdata == 'True':
        collect_data = threading.Thread(target=collector.collect_data, args=(driver.get_commands,),daemon=True)
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
    for index, thread in enumerate(threads):
        thread.join()

    pass

if __name__=="__main__":
        main()
