
'''
Class Files for ImageProc Class
Captures Images through Raspberry Pi camera
Captures Command Signals
#Combines [Image, Command]
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
import threading


def get_command():
	return np.random.randn(2)

def get_class():
	return 1


class ImageProc(object):
	def __init__(self,args):
		# intitalise parameters
		params = load(open('camera.yaml').read(), Loader=Loader)
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
		self.image_array = PiRGBArray(camera, size=camera.resolution)
		self._lock=threading.RLock()
		self.frame_num = 0
		pass

	def collect_data_new(self,get_class=get_class,get_commands=get_commands):
		'''
		collects example data and stores to file in separate directories
		Classifies the drive/steer data into 7 classes and stores them in relevant Directories
		'''

		#create requisite Directory
		if self.args.selfdrive == 'True':
			dirName = self.params['self_drive_dirname']
		else:
			dirName = self.params['training_dirname']

		rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
		Max_Frames = int(self.args.record_time)*int(self.args.framerate)
		if self.args.labels == 'True':
			labels=np.zeros(Max_Frames)
		else:
			for class_dirname in range(1,8):
				try:
					os.makedirs(os.path.join(dirName,str(class_dirname)))
				except FileExistError:
					print('directories exist')

		print('Max Frames', Max_Frames)
		frame_num = 0
		for frame in self.camera.capture_continuous(rawCapture, format="bgr" , use_video_port=True):
			image = rawCapture.array
			if self.args.labels == 'True':
				img_filename = os.path.join(dirName,'data{0}_{1:04d}'.format(self.args.example,frame_num))
				cmd_filename = os.path.join(dirName,'cmd{0}_{1:04d}'.format(self.args.example,frame_num))
				labels[frame_num]=get_class()
				cmd = [get_class(),get_commands()]
				np.save(img_filename,image,allow_pickle=True)
				np.save(cmd_filename,cmd,allow_pickle=True)

			else:
				class_dirname = os.path.join(dirName,str(get_class()))
				img_filename = os.path.join(class_dirname,'data{0}_{1:04d}'.format(self.args.example,frame_num))
				np.save(img_filename,image,allow_pickle=True)

			# clear the stream in preparation for the next frame
			rawCapture.truncate(0)
			print('Class Num', get_class(), 'Frame ',frame_num)
			frame_num+=1
			if frame_num == Max_Frames:
				break
		if self.args.labels == 'True':
			np.save(os.path.join(dirName,self.args.example),\
			labels,allow_pickle=True)
		print('Finished Collecting Data')
		self.camera.close()
		pass

	def collect_data_old1(self,get_commands=get_command):
		'''
		collects example data and stores to file
		'''
        	#create requisite Directory
		if self.args.selfdrive == 'True':
			dirName = self.params['self_drive_dirname']
		else:
			dirName = self.params['examples_dirname']
		dirName += self.args.example

		try:
    	  	# Create target Directory
		  os.mkdir(dirName)
		  print("Directory " , dirName ,  " Created ")
		except FileExistsError:
		  print("Directory " , dirName ,  " already exists")
		rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
		Max_Frames = int(self.args.record_time)*int(self.args.framerate)
		print('Max Frames', Max_Frames)
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
			print('stored frame_num', frame_num)
			frame_num+=1
			if frame_num == Max_Frames:
				break
		print('Finished Collecting Data')
		pass
	'''
	def collect_data_old2(self,get_commands=get_command):

		#collects example data and stores to file in separate directories

		#create requisite Directory
		if self.args.selfdrive == 'True':
			dirName = self.params['self_drive_dirname']
		else:
			dirName = self.params['examples_dirname']
		dirName += self.args.example

		# Create target Directories

		try:
		  os.mkdir(dirName)
		  print("Directory " , dirName ,  " Created ")
		except FileExistsError:
		  print("Directory " , dirName ,  " already exists")

		try:
		  os.mkdir(dirname+'/X')
		  os.mkdir(dirname+'/Y')
	  	except FileExistsError:
		  print("Directory " , dirName+'/X' ,  " already exists")

		rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
		Max_Frames = int(self.args.record_time)*int(self.args.framerate)
		print('Max Frames', Max_Frames)
		frame_num = 0
		for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			image = rawCapture.array
			commands = get_commands()
			#combine with command data into example
			#data = [image, commands]
			#write to Files
			img_filename = './'+dirName+'/X/'+'data%04d'%frame_num
			cmd_filename = './'+dirName+'/Y/'+'cmd%04d'%frame_num
			np.save(img_filename,image,allow_pickle=True)
			np.save(cmd_filename,commands,allow_pickle=True)
				# clear the stream in preparation for the next frame
			rawCapture.truncate(0)
			print('stored frame_num', frame_num)
			frame_num+=1
			if frame_num == Max_Frames:
				break
		print('Finished Collecting Data')
		pass
	'''

	def collect_data(self,get_class=get_class):
		'''
		collects example data and stores to file in separate directories
		Classifies the drive/steer data into 9 classes and stores them in relevant Directories
		'''
		#create requisite Directory
		if self.args.selfdrive == 'True':
			dirName = self.params['self_drive_dirname']
		else:
			dirName = self.params['examples_dirname']
		dirName += self.args.example

		# Create target Directories

		try:
		  os.mkdir(dirName)
		  print("Directory " , dirName ,  " Created ")
		except FileExistsError:
			if os.listdir(dirName): #directory has data
				print("Directory " , dirName ,  " already exists: data deleted")
				try :
					os.system('rm -r '+dirName+'/*')
				except:
					pass
			else:
				print('Error in creating Directory')
		# now make the different class directories
		for class_dirname in range(1,10):
			try:
		  		os.mkdir(dirName+'/%d'%class_dirname)
			except FileExistsError:
				print("Directory " , dirName+'/1' ,  " already exists: cleaned existing data")

		rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
		Max_Frames = int(self.args.record_time)*int(self.args.framerate)
		print('Max Frames', Max_Frames)
		frame_num = 0
		for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			image = rawCapture.array
			classification = get_class()

			#write to File
			img_filename = './'+dirName+'/%d/'%classification+'data%04d'%frame_num
			np.save(img_filename,image,allow_pickle=True)
			# clear the stream in preparation for the next frame
			rawCapture.truncate(0)
			print('stored frame_num', frame_num)
			frame_num+=1
			if frame_num == Max_Frames:
				break
		print('Finished Collecting Data')
		pass



		def capture_image(self): #is this used at all?
			'''
			capture frames one by one and store them
			'''
			rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
			Max_Frames = self.args.record_time*self.args.framerate
			print('Max Frames', Max_Frames)
			frame_num = 0
			for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
				with self._lock:
					self.image_array = rawCapture
					self.frame_num+=1
				print('Captured Frame',frame_num)
				frame_num +=1
				rawCapture.truncate(0)
				if frame_num == Max_Frames:
					break

		def get_frame_num(self):
			with self._lock:
				return self.frame_num

		def set_frame_num(self,frame_num):
			with self._lock:
				self.frame_num=frame_num
			pass


		def get_image(self):
			'''
			get stored Images
			'''
			with self._lock:
				return self.image_array.array


def main():
    parser = argparse.ArgumentParser(description='Capture Video and Content Frames')
    parser.add_argument('--example', default='1')
    parser.add_argument('--record_time', default=10)
    parser.add_argument('--framerate',default=30)
    parser.add_argument('--selfdrive',default=False)
    parser.add_argument('--collectdata',default=False)
    args = parser.parse_args()
    c = ImageProc(args)
    c.collect_data()
if __name__=="__main__":
        main()
