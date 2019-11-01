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
from flask import Flask, request
import atexit
import pz
import chaturcar
import imageproc
import models

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
    #start the flask server for reading commands - this is the main thread
    app = Flask(__name__)
    app.route("/")(driver.web_interface)
    app.route("/recv_commands")(driver.receive_commands)
    app.route("/stop")(driver.stop)
    app.run(host= args.hostname,port=args.port, debug=True)

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
