
'''
Class Files for ImageProc Class
Captures Images through Raspberry Pi camera
Captures Command Signals
Combines [Image, Command]
pickles them and stores to a folder with name Examples%d or Test%d (input string)
Manish Mahajan
25 Sep 2019
'''
# import the necessary packages
from yaml import load, Loader
from picamera.array import PiRGBArray
from picamera import PiCamera
import os
import time
import numpy as np
import argparse


def get_command():
	return np.random.randn(2)

class ImageProc(object):
    def __init__(self,args):
        # intitalisse parameters
        params = load(open('camera.yaml').read(), Loader=Loader)
    	# initialize the camera and set output
    	camera = PiCamera()
    	camera.resolution = params['resolution']
    	camera.framerate = args.framerate
    	camera.rotation = params['rotation']
    	camera.iso = params['iso'] #800 for indoors, 200 outdoors
        # allow the camera to warmup
    	time.sleep(2)
        #Now Set Fixed Camera Parameters
    	camera.exposure_mode = params['exposure_mode']
    	g = camera.awb_gains
    	camera.awb_mode = params['awb_mode']
    	camera.awb_gains = g
        self.camera = camera
        self.args = args
	self.image_array = PiRGBArray(camera, size=camera.resolution)
	self._lock=threading.RLock()
	self.frame_num = 0
        pass


    def collect_data(self,get_commands=get_command):
	'''
	collects example data and stores to file
	'''
        #create requisite Directory
        if args.selfdrive == 'True':
            dirname = params['self_drive_dirname']
        else:
            dirname = params['examples_dirname']
        dirname += args.example
    	try:
    	  # Create target Directory
    	  os.mkdir(dirName)
    	  print("Directory " , dirName ,  " Created ")
    	except FileExistsError:
    	  print("Directory " , dirName ,  " already exists")

	rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
    	Max_Frames = self.args.record_time*self.camera.framerate
    	frame_num = 0

    	for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    		image = rawCapture.array
    		commands = get_commands()
    		#combine with command data into example
    		data = [image, commands]
    		#write to File
    		filename = './'+dirName+'/'+'data%04d'%frame_num
    		np.save(filename,data,allow_pickle=True)
    		# clear the stream in preparation for the next frame
    		rawCapture.truncate(0)
    		frame_num+=1
    		if frame_num == Max_Frames:
    			break
        pass

    def capture_image(self):
		'''
		capture frames one by one and store them
		'''
		rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
		Max_Frames = self.args.drive_time*self.camera.framerate
		frame_num = 0
		for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			with self._lock:
				self.image_array = rawCapture
				self.frame_num+=1
			frame_num +=1
	    		rawCapture.truncate(0)
	    		if frame_num == Max_Frames:
	    			break

		pass

    def get_frame_num(self):
		with self._lock:
			return self.frame_num

    def get_image(self):
		'''
		get stored Images
		'''
		with self._lock:
			return self.image_array.array
		pass






def main():
    parser = argparse.ArgumentParser(description='Capture Video and Content Frames')
    parser.add_argument('--example', default='1')
    parser.add_argument('--record_time', default=10)
    parser.add_argument('--framerate',default=30)
    parser.add_argument('--selfdrive',default=False)
    parser.add_argument('--collectdata',default=False)
    args = parser.parse_args()
    c = CollectData(args)
    c.collect_data()
if __name__=="__main__":
        main()
