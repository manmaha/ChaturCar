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
import picon
import FNGcontroller

class PiconCar(picon.Robot):
    '''Special subclass of picon.Robot class with a steering motor and drive motor
    Also using PiconZero and camera
    Picon Motor A(0) set as steering motor, Motor B(1) set as driving motor
    using the pz robot class without the other features
    Speeds are between -1 and +1
    '''
    def __init__(self):
        super(PiconCar,self).__init__()
        pass
    def drive(self,commands):
        # this is specific to this piconzero and chassis set up
        #steer_speed = commands[0]
        #drive_speed = commands[1]
        self.set_motors(commands)
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

class FNGCar(FNGcontroller.SteerDriveCar):
    ''' Special Case of FNG Controller Steer Drive Car,
        scales speed from -1/+1 to -100/+100
    '''
    def __init__(self):
        super(FNGCar,self).__init__()
        pass

    def drive(self,commands):
        # this is specific to this FNGDriver and chassis set up
        #motor A is inverted, also scaling from -1/+1 to -100/100
        commands[1]=-commands[1]
        super(FNGCar,self).drive([100.0*c for c in commands])
        pass

    def get_speed(self):
        #reverse the above function
        speed = [s/100.0 for s in super(FNGCar,self).get_speed()]
        speed[1]=-speed[1]
        return speed


class Driver(object):
    def __init__(self,car,args):
        self.car = car
        self.args = args
        self._lock=threading.RLock()
        pass

class ChaturDriver(Driver):
        def __init__(self,car,args):
            super(ChaturDriver,self).__init__(car,args)
            #set up Categories
            steer = args.max_steer
            self.categories = {1:-0.833*steer,2:-0.5*steer,\
                                3:-0.167*steer,4:0.0,\
                                5:0.167*steer,6:0.5*steer,\
                                7:0.833*steer}
            #Start Driving and Check if driver needs to Exit
            self.driving = True
            car.forward(args.max_drive)
            pass

        def stop_driving(self):
            with self._lock:
                self.driving = False
                print('Stopped Driving')
            self.car.stop()
            self.car.cleanup()

        def is_driving(self):
            with self._lock:
                return self.driving

        def stop(self):
            #self.send_commands([0, - self.get_commands()[1]])
            #time.sleep(0.25)
            self.car.stop()
            #return self.web_interface()

        # Command Methods
        def send_commands(self,commands):
            '''
            sends commands to the car
            commands are [steer_speed, drive_speed]
            '''
            with self._lock:
                self.car.drive(commands)
            #print('sent to car ',commands)

        def get_commands(self):
            '''
            get commanded speeds from car
            commands are [steer_speed, drive_speed]
            '''
            with self._lock:
                #return self.commands
                return self.car.get_speed()

        def get_category(self):
            '''
            Define Classification of Commands to be used in Learning Model
            		Drive +1 Steer -1 : Class 1
            		Drive +1 Steer -2/3 : Class 2
            		Drive +1 Steer -1/3 : Class 3
            		Drive +1 Steer 0 : Class 4
            		Drive +1 Steer +1/3 : Class 5
                    Drive +1 Steer +2/3 : Class 6
                    Drive +1 Steer +1 : Class 7
                    returns an int
            '''
            category = 1
            sensitivity = 0.08
            steer_value, _ = self.get_commands()
            # find +1,-1,0 Classification
            if steer_value > 0.67*self.args.max_steer:
                category = 7
            elif steer_value > 0.33*self.args.max_steer:
                category = 6
            elif steer_value > sensitivity:
                category = 5
            elif steer_value >= -sensitivity:
                category = 4
            elif steer_value > -0.33*self.args.max_steer:
                category = 3
            elif steer_value > -0.67*self.args.max_steer:
                category = 2
            return category

        def get_commands_from_category(self,category):
            return [self.args.max_drive,self.categories.get(category)]

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
        def self_driver(self,collector,is_driving):
            import models
            #Choose Model
            if self.args.model == 'Trained':
                model = Models.Trained_Model(self.args)
            else:
                model = Models.Naive_Model(self.args)
            #Max_Frames = self.args.drive_time*self.args.framerate
            #for frame_num in range(Max_Frames):
            while is_driving():
                while frame_num >= collector.get_frame_num(): #new frame has not been posted
                    pass
                #new image seen
                data = collector.get_image_array()
                category = model.predict_category(data)
                self.send_commands(self.get_commands_from_category(category))



        #utility methods
        def cleanup(self):
            self.car.cleanup()
            return sys.exit(0)

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
    parser.add_argument('--avg_steer',default=params['avg_steer'])
    parser.add_argument('--avg_drive',default=params['avg_drive'])
    parser.add_argument('--labels', default=params['labels'])

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
