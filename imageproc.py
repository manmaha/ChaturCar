
'''
Class Files for ImageProc Class
Captures Images through Raspberry Pi camera
Captures Command Signals
Classifies Images in Classes 1-7
Stores Images in Train/1-7 directories
Manish Mahajan
9 Dec 2019
'''
# import the necessary packages
from yaml import load, Loader
from picamera.array import PiRGBArray
from picamera import PiCamera
import os
import io
import time
import numpy as np
import argparse
import threading

#Testing Functions
def get_commands():
	return np.random.randn(2)

def get_category():
	return 1
#####

class ImageProc(object):
	def __init__(self,args,params):
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
		self.params = params
		self._lock=threading.RLock()
		pass

	def collect_data(self,get_category=get_category,get_commands=get_commands):
		'''
		collects example data and stores to file in separate directories
		Classifies the drive/steer data into 7 classes and stores them in relevant Directories
		'''

		#create requisite Directory
		if self.args.selfdrive == 'True':
			dirName = self.params['self_drive_dirname']
		else:
			dirName = self.params['training_dirname']

		Max_Frames = int(self.args.record_time)*int(self.args.framerate)


		if self.args.labels == 'True':
			labels=[]
		else:
			for class_dirname in range(1,8):
				try:
					os.makedirs(os.path.join(dirName,str(class_dirname)))
				except FileExistsError:
					print('directories exist')

		with io.BytesIO() as stream:
			frame_num = 0
			for frame in self.camera.capture_continuous(stream, format="jpeg" , use_video_port=True):
				if self.args.labels == 'True':
					filename = os.path.join(dirName,'img{0}_{1:04d}.jpg'.format(self.args.example,frame_num))
					labels.append([get_category(),get_commands()])
				else:
					class_dirname = os.path.join(dirName,str(get_category()))
					filename = os.path.join(class_dirname,'img{0}_{1:04d}.jpg'.format(self.args.example,frame_num))
				#Write to File
				with open(filename,"wb") as imagefile:
					imagefile.write(stream.getbuffer())
				# clear the stream in preparation for the next frame
				stream.seek(0)
				stream.truncate(0)
				#print('Class Num', get_category(), 'Frame ',frame_num)
				frame_num+=1
				if frame_num == Max_Frames:
					break


		print('Finished Collecting Data')
		self.camera.close()
		pass



def main():
	params = load(open('ChaturCar.yaml').read(), Loader=Loader)
	parser = argparse.ArgumentParser(description='Capture Video and Content Frames')
	parser.add_argument('--example', default=params['example'])
	parser.add_argument('--record_time', default=params['record_time'])
	parser.add_argument('--framerate',default=params['framerate'])
	parser.add_argument('--selfdrive',default=params['selfdrive'])
	parser.add_argument('--collectdata',default=params['collectdata'])
	parser.add_argument('--labels', default=params['labels'])
	args = parser.parse_args()
	c = ImageProc(args,params)
	c.collect_data()
if __name__=="__main__":
        main()
