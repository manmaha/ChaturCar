
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
from PIL import Image

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
		self.image_array = PiRGBArray(camera, size=params['resolution'])
		self.stream = io.BytesIO()
		self.frame_num = 0
		self.Max_Frames = int(args.record_time)*int(args.framerate)
		#create requisite Directories
		if args.selfdrive == 'True':
			self.dirName = params['self_drive_dirname']
		else:
			self.dirName = params['training_dirname']
		if args.labels == 'True':
			self.labels=[]
		else:
			for class_dirname in range(1,8):
				try:
					os.makedirs(os.path.join(self.dirName,str(class_dirname)))
				except FileExistsError:
					print('directories exist')
		pass

	def collect_data(self,get_category=get_category,get_commands=get_commands):
		'''
		collects example data and stores to file in separate directories
		Classifies the drive/steer data into 7 classes and stores them in relevant Directories
		'''
		with io.BytesIO() as stream:
			frame_num = 0
			for _ in self.camera.capture_continuous(stream,format="jpeg",use_video_port=True):
				category = get_category()
				if self.args.labels == 'True':
					filename = os.path.join(self.dirName,'img{0}_{1:d}_{2:04d}.jpg'\
					.format(self.args.example,category,frame_num))
					self.labels.append([category,get_commands()])
				else:
					class_dirname = os.path.join(self.dirName,str(category))
					filename = os.path.join(class_dirname,'img{0}_{1:d}_{2:04d}.jpg'\
					.format(self.args.example,category,frame_num))
				#Write to File
				with open(filename,"wb") as imagefile:
					imagefile.write(stream.getbuffer())
				# clear the stream in preparation for the next frame
				stream.seek(0)
				stream.truncate(0)
				print('Category', category,'Commands', get_commands(), 'Frame ',frame_num)
				frame_num+=1
				if frame_num == self.Max_Frames:
					break
		print('Finished Collecting Data')
		self.cleanup()
		pass

	def capture_image(self,get_category=get_category,get_commands=get_commands):
			'''
			capture images for the self driver; also stores them in files for later analysis
			'''
			with picamera.array.PiRGBArray(self.camera) as stream:
				frame_num = 0
				for _ in self.camera.capture_continuous(stream,format="rgb",use_video_port=True):
					category = get_category()
					with self._lock:
						self.image_array=stream
						self.frame_num+=1
					if self.args.labels == 'True':
						filename = os.path.join(self.dirName,'img{0}_{1:d}_{2:04d}.jpg'\
						.format(self.args.example,category,frame_num))
						self.labels.append([category,get_commands()])
					else:
						class_dirname = os.path.join(self.dirName,str(category))
						filename = os.path.join(class_dirname,'img{0}_{1:d}_{2:04d}.jpg'\
						.format(self.args.example,category,frame_num))
					#Write to File, using PIL Image class definition
					Image.fromarray(stream.array).save(filename)
					# clear the stream in preparation for the next frame
					stream.truncate(0)
					frame_num+=1
					if frame_num == self.Max_Frames:
						break
			print('Finished Recording Images')
			self.cleanup()
			pass

	def cleanup(self):
		self.camera.close()
		if self.labels : #labels has Data
			np.save(os.join(self.dirName,'labels_{0}.npy'\
				.format(self.args.example)),self.labels,allow_pickle=True)
		pass

	def get_frame_num(self):
		with self._lock:
			return self.frame_num

	def set_frame_num(self,frame_num):
		with self._lock:
			self.frame_num=frame_num
		pass

	def set_image(self,image_array):#PIRGBArray):
		with self._lock:
			self.image_array=image_array

	def get_image(self):
		with self._lock:
			return self.image_array.array




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
