#!/usr/bin/env python3
''' ChaturCar - Clever Car Class
Self Driving Car based on Picon Zero, Camera, Edge TPU and RC Car Chassis
Car has a steering motor and a driving motor

Steering and Drive Commands for Training are received through a Web GUI
Manish Mahajan
25 September 2019
'''

import logging
import time
import argparse
import signal
import sys
import threading
from yaml import load, Loader
import atexit
import pz

class ChaturCar(pz.Robot):
    '''Special subclass of pz.Robot class with a steering motor and drive motor
    Also using PiconZero and camera
    Picon Motor A(0) set as steering motor, Motor B(1) set as driving motor
    using the pz robot class without the other features
    Speeds are between -1 and +1
    '''
    def __init__(self):
        super(ChaturCar,self).__init__()
        pass
    def drive(self,commands):
        # this is specific to this piconzero and chassis set up
        steer_speed = commands[0]
        drive_speed = commands[1]
        self.set_motors(steer_speed,drive_speed)
        pass
    def forward(self,speed=1.0):
        self.drive([0,speed])
    def reverse(self,speed=1.0):
        self.drive([0,-speed])
    def steer_left(self,speed=1.0):
        self.drive([-speed,0])
    def steer_right(self,speed=1.0):
        self.drive([speed,0])
    def test(self):
        print('Testing Car')
        print('Forward 1 seconds')
        self.forward(0.25)
        time.sleep(1)
        self.stop()
        print('Backward 1 seconds')
        self.reverse(0.25)
        time.sleep(1)
        self.stop()
        print('Test Steering')
        self.steer_left()
        time.sleep(1)
        self.steer_right()
        time.sleep(1)
        self.stop()
        print('Test Circle')
        self.drive([0.50,0.50])
        time.sleep(1)
        self.stop()
        self.drive([-0.50,-0.50])
        time.sleep(1)
        self.stop()

class Driver(object):
    def __init__(self,car,args):
        self.car = car
        self.args = args
        pass

class ChaturDriver(Driver):
        def __init__(self,car,args):
            super(ChaturDriver,self).__init__(car,args)
            #Initialise Driver
            self.commands = [0,0] #initialise commands
            self._lock=threading.RLock()
            if args.selfdrive == 'True':
                #set up selfdrive
                pass
            self.args = args
            pass
        def stop(self):
            self.send_commands([0, - self.get_commands()[1]])
            time.sleep(0.25)
            self.car.stop()
            return self.web_interface()
        # Command Methods
        def send_commands(self,commands):
            '''
            sends commands to the car
            commands are [steer_speed, drive_speed]
            '''
            with self._lock:
                self.car.drive(commands)
            print('sent to car ',commands)
            pass

        def get_commands(self):
            '''
            get commanded speeds from pz.car
            commands are [steer_speed, drive_speed]
            '''
            with self._lock:
                speed = self.car.get_speed()
            commands = [speed[0],speed[1]]
            return commands

        #Web Receiver methods
        #@app.route("/")
        def web_interface(self):
            # html file is in ChaturCar.html
            html = open("ChaturCar.html")
            response = html.read().replace('\n', '')
            html.close()
            return response

        #@app.route("/recv_commands")
        def receive_commands(self):
            '''
            Receive Commands from interface
            Send them to Car
            '''
            try:
                drive_speed = float(request.args.get("drive_speed"))
                steer_speed = float(request.args.get("steer_speed"))
                commands = [steer_speed,drive_speed]
            except:
                return "Bad Input"
                print('Bad speed input')
            else:
                #print('commands',commands)
                self.send_commands(commands)

        # Self Driver
        def self_driver(self,collector):
            #Choose Model
            model = Models.Naive_Model(self.args)
            Max_Frames = self.args.drive_time*self.args.framerate
            for frame_num in range(Max_Frames):
                while frame_num >= collector.get_frame_num(): #new frame has not been posted
                    pass
                #new image seen
                data = collector.get_image()
                commands = model.generate_commands(data)
                self.send_commands(commands)



        #utility methods
        def exit_driver(self):
            return sys.exit(0)

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

    car = ChaturCar()
    driver =ChaturDriver(car,args)
    car.test()

if __name__=="__main__":
        main()
