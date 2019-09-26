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
from ImageProc import ImageProc
import Models

class ServerThread(threading.Thread):
'''
Flask Server Thread designed for clean exit
'''
    def __init__(self, app, args):
        threading.Thread.__init__(self)
        self.srv = make_server(args.hostname, args.port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

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
        # this is specific to this piconzero and chassis set up
        steer_speed = commands[0]
        drive_speed = -commands[1]
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

        # Command Methods
        def send_commands(self,commands):
            '''
            sends commands to the car
            commands are [steer_speed, drive_speed]
            '''
            with self._lock:
                self.car.drive(commands)
            pass

        def get_commands(self):
            '''
            get commanded speeds from pz.car
            commands are [steer_speed, drive_speed]
            '''
            with self._lock:
                speed = self.car.get_speed()

            commands = [speed[1],-speed[0]]
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
                print('commands',commands)
                self.send_commands(commands)
                return commands

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
        server.shutdown()
        pass

    car = ChaturCar()
    car.test()
    driver =ChaturDriver(car,args)

    if args.selfdrive == 'True' or args.collectdata == 'True':
        collector = ImageProc(args)

    #start the threaded processes
    threads = list()
    '''
    Thread to receive commands goes here
    '''
    #start the flask server for reading commands - this is the main thread
    app = Flask(__name__)
    app.route("/")(driver.web_interface)
    app.route("/recv_commands")(driver.receive_commands)
    app.route("/stop")(car.stop)
    app.route("/exit")(lambda:sys.exit(0))
    server = ServerThread(app,args)
    server.start()
    threads.append(server)

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
        capture_image = threading.Thread(target=collector.capture_image,daemon=true)
        capture_image.start()
        threads.append(capture_image)

        self_drive = threading.Thread(target=driver.self_drive,args=(collector,)daemon=true)
        self_drive.start()
        threads.append(self_drive)

    #join all threads
    for index, thread in enumerate(threads):
        thread.join()

    pass




    #app.run(host= args.hostname,port=args.port, debug=False)
'''
if __name__=="__main__":
        main()
