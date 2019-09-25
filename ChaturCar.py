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
from flask import Flask
from flask import request
import atexit
from werkzeug.serving import make_server
import pz

'''
class Car(object):
    def __init__(self):
        pass
    def drive(self,commands):
        #implemented specific to each car subclass
        pass
    def stop(self):
        self.drive([0,0])
        pass
'''

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
        steer_speed = commands[0]
        drive_speed = commands[1]
        self.set_motors(drive_speed,steer_speed)
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
        print('Forward 3 seconds')
        self.forward()
        time.sleep(3)
        self.stop()
        print('Backward 3 seconds')
        self.reverse()
        time.sleep(3)
        self.stop()
        print('Test Steering')
        self.steer_left()
        time.sleep(1)
        self.steer_right()
        time.sleep(1)
        self.stop()
        print('Test Circle')
        self.drive([0.50,0.50])
        time.sleep(3)
        self.stop()
        self.drive([-0.50,-0.50])
        time.sleep(3)
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
            if args.collectdata == 'True':
                #Set Up collect_data
                from CollectData import CollectData
                self.collector = CollectData(args)
                pass
            if args.selfdrive == 'True':
                #set up selfdrive
                pass
            self.args = args
            pass

        # Command Methods
        def send_commands(self):
            '''
            sends commands to the car after picking them up from the right interface
            commands are [steer_speed, drive_speed]
            '''
            commands = self.get_commands()
            self.car.drive(commands)
            pass
        def get_commands(self):
            '''
            get commands from interface or from self Driver
            commands are [steer_speed, drive_speed]
            '''
            if self.args.selfdrive == 'True':
                commands = self.generate_commands()
            else:
                commands = self.receive_commands()
            return commands
        def receive_commands(self):
            commands = [0.0,0.0] #initialise Commands
            '''
            receive commands from transmitting interface
            '''
            return commands
        def generate_commands(self):
            commands = [0.0,0.0] #initialise Commands
            '''
            generate commands from self driving model
            '''
            return commands

        #Data Capture Methods
        def collect_data(self):
            self.collector.collect_data(self.getcommands)
            pass

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
    parser.add_argument('--example', default=params['example'])
    parser.add_argument('--framerate',default=params['framerate'])
    args = parser.parse_args()

    car = ChaturCar()
    car.test()


    # Cleanup done at exit

    @atexit.register
    def shutdownChaturCar():
        print('EXITING')
        car.stop()
        #car.cleanup()
        #server.shutdown()
        pass
''' Need to save space for Button Pins, Use Later
        #Buttons
        button_pin = params['button_pin']
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        #set up button handling
        GPIO.add_event_detect(button_pin, GPIO.RISING, bouncetime = 200)
        GPIO.add_event_callback(button_pin, PiOde.toggle_roaming)
        print('PiOde Set Up Complete')
'''

'''
    #start the threaded processes
    threading.Thread(target=d.sense,daemon=True).start()

    #start the flask server
    app = Flask(__name__)
    #app.add_url_rule('/','web_interface',d.web_interface)
    #app.add_url_rule('/read_vel','read_vel',d.read_vel)

    app.route("/")(d.web_interface)
    app.route("/read_vel")(d.read_vel)
    app.route("/stop")(d.stop)
    #app.route("/exit")(lambda:sys.exit(0))

    app.run(host= args.hostname,port=args.port, debug=False)
'''
if __name__=="__main__":
        main()
