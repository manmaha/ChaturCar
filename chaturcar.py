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

            avg_steer, avg_drive = self.args.avg_steer, self.args.avg_drive
            self.classes = {1:[0,avg_drive],2:[-avg_steer,avg_drive],\
            3:[avg_steer,avg_drive],7:[0,0],\
            4:[0,-avg_drive],5:[-avg_steer,-avg_drive],6:[avg_steer,-avg_drive]}

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

        def get_class(self):
            '''
            Define Classification of Commands to be used in Learning Model
            		Drive +1 Steer 0 : Class 1
            		Drive +1 Steer -1 : Class 2
            		Drive +1 Steer +1 : Class 3
            		Drive -1 Steer 0 : Class 4
            		Drive -1 Steer -1 : Class 5
            		Drive -1 Steer +1 : Class 6
            		Drive 0 : Class 7
            '''
            sensitivity = 0.15
            drive_value, steer_value = self.get_commands()
            # find +1,-1,0 Classification
            if drive_value > sensitivity:
                drive = 1
            elif drive_value > -sensitivity:
                drive = 0
                return 7
            else:
                drive = -1

            if steer_value > sensitivity:
                steer = 1
            elif steer_value > -sensitivity:
                steer = 0
            else:
                steer = -1
            # Now classify

            if drive == 1:
                if steer == 0:
                    return 1
                elif steer == -1:
                    return 2
                else:
                    return 3

            elif drive == -1:
                if steer == 0:
                    return 4
                elif steer == -1:
                    return 5
                else:
                    return 6

            else:
                return 7
                '''
                if steer == 0:
                    return 7
                elif steer == -1:
                    return 8
                else:
                    return 9
                '''


        def get_commands_from_class(self,classification):
            return self.classes.get(classification)

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
                classification = model.generate_class(data)
                self.send_commands(self.get_commands_from_class(classification))



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
    parser.add_argument('--avg_steer',default=params['avg_steer'])
    parser.add_argument('--avg_drive',default=params['avg_drive'])
    parser.add_argument('--labels', defalut=params['labels'])
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
