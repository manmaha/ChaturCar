import time
import picamera
import os
import io

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 1
    camera.rotation = 180
    time.sleep(1)
    frame_num = 0
    with io.BytesIO() as my_stream:
        dir = '1'
        for frame in camera.capture_continuous(my_stream, format="jpeg" , use_video_port=True):
            if frame_num > 9:
                dir = '2'
            filename = os.path.join(os.path.join('images',dir),'image{0:02d}.jpg'.format(frame_num))
            print(filename)
            with open(filename,"wb") as imagefile:
                imagefile.write(my_stream.getbuffer())
            my_stream.seek(0)
            my_stream.truncate(0)
            frame_num +=1
            if frame_num == 20:
                break
