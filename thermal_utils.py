import sys
sys.path.append("/home/ohdeer/venv/lib/python3.11/site-packages")
sys.path.append("/home/ohdeer/pysenxor-master/")
import os
import signal
import time
import logging
import serial
import numpy as np
import cv2 as cv
from datetime import datetime

from senxor.mi48 import MI48, format_header, format_framestats
from senxor.utils import data_to_frame, remap, cv_filter,\
                         cv_render, RollingAverageFilter,\
                         connect_senxor


class Thermal():
    def __init__(self):

        self.startup()

        # initiate continuous frame acquisition
        with_header = True
        mi48.start(stream=True, with_header=with_header)

        self.logger
        self.recorder = Recorder()
        self.recording = False
        self.rec_length = 15
        #self.frame
        self.deer_pos = -1
        self.lock = False

        self.read_frame()

    def startup(self):
        # Copied from original source code

        # This will enable mi48 logging debug messages
        self.logger = logging.getLogger(__name__)
#        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

        # Make the a global variable and use it as an instance of the mi48.
        # This allows it to be used directly in a signal_handler.
        global mi48

        # define a signal handler to ensure clean closure upon CTRL+C
        # or kill from terminal
        def signal_handler(sig, frame):
            """Ensure clean exit in case of SIGINT or SIGTERM"""
            self.logger.info("Exiting due to SIGINT or SIGTERM")
            mi48.stop()
            cv.destroyAllWindows()
            self.logger.info("Done.")
            sys.exit(0)

        # Define the signals that should be handled to ensure clean exit
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


        # Make an instance of the MI48, attaching USB for 
        # both control and data interface.
        # can try connect_senxor(src='/dev/ttyS3') or similar if default cannot be found
        mi48, connected_port, port_names = connect_senxor()
        print(f"mi48: {mi48}, connected_port: {connected_port}, port_names: {port_names}")

        # print out camera info
        self.logger.info('Camera info:')
        self.logger.info(mi48.camera_info)

        # set desired FPS
        if len(sys.argv) == 2:
            STREAM_FPS = int(sys.argv[1])
        else:
            STREAM_FPS = 15
        mi48.set_fps(STREAM_FPS)

        # see if filtering is available in MI48 and set it up
        mi48.disable_filter(f1=True, f2=True, f3=True)
        mi48.set_filter_1(85)
        mi48.enable_filter(f1=True, f2=False, f3=False, f3_ks_5=False)
        mi48.set_offset_corr(0.0)

        mi48.set_sens_factor(100)
        mi48.get_sens_factor()


    def read_frame(self):
        # Read the frame
        data, header = mi48.read()

        if data is None:
            self.logger.critical('NONE data received instead of GFRA')
            mi48.stop()
            sys.exit(1)
        # Log the header and frame stats
        elif header is not None:
            self.logger.debug('  '.join([format_header(header),
                                    format_framestats(data)]))
        # else:
        #     self.logger.debug(format_framestats(data))
        
        self.frame = data
    
    def process_frame(self):
        
        # preset par value
        par = {'blur_ks':3, 'd':5, 'sigmaColor': 27, 'sigmaSpace': 27}

        self.dminav = RollingAverageFilter(N=10)
        self.dmaxav = RollingAverageFilter(N=10)

        # normalizes colors based on the min and max temp of the frame
        min_temp = self.dminav(self.frame.min())  # + 1.5
        max_temp = self.dmaxav(self.frame.max())  # - 1.5
        frame = data_to_frame(self.frame, (80,62), hflip=False)
#        frame = np.rot90(frame, 1).copy()

        raw = frame.astype(np.uint8)
        # print(f'raw -  min:{np.min(raw)}, max:{np.max(raw)}')

        not_noise = True
        if frame.max() - frame.min() < 10: # note: adjust this value to change threshold for noise
            not_noise = False 

        # clip bottom values if the difference is too high
        if max_temp - min_temp > 20:
            min_temp = max_temp - 20

        frame = np.clip(frame, min_temp, max_temp).astype(np.uint8)
        filt_uint8 = cv_filter(remap(frame), par, use_median=True,
                            use_bilat=True, use_nlm=False)
        
        normalized_frame = ((frame - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)


        # img = filt_uint8.astype(np.uint8)
        img = normalized_frame.astype(np.uint8)
        bounding = img.copy()

        if not_noise:
            _,thresh = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
            contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            c_filtered = []

            # filter out contours that are too small
            min_area = 20  # Adjust this value
            max_area = 2300
            for contour in contours:
                area = cv.contourArea(contour)
                if area > min_area and area < max_area:
                    c_filtered.append(contour)

            # for contour in c_filtered:
            # # cv.drawContours(bounding, contour,  -1, (0, 0, 255), 5)
            #     x, y, w, h = cv.boundingRect(contour)
            #     cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 1)  # draw box

            if len(c_filtered) >= 1:

        #     cv.drawContours(bounding, contour,  -1, (0, 0, 255), 5)
                contour = c_filtered[0]
                x, y, w, h = cv.boundingRect(contour)
                cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 1)  # draw box
                
                centroid_x = int(x + w/2) # horizontal centroid wrt pixels 0-80
                centroid_y = int(y + h/2) # verticle centroid
                # print(f'centroid:{centroid_x}')
                cv.circle(bounding, (centroid_x, centroid_y), 3, (255, 0, 0), 2)
                # print(f'contour - x:{x}, y:{y}, w:{w}, h:{h}')
                # print(f'area: {cv.contourArea(contour)}')
                # print('cycle done')

                self.lock = True
                self.deer_pos = centroid_y

                if not self.recording:
                    self.recorder = Recorder()
                    self.recording = True
            else:
                self.lock = False
                self.deer_pos = -1
        # else:
        #     pass

        if self.recording:
            self.recorder.write_bbox(bounding)

            if self.recorder.get_time() >= self.rec_length:
                self.recorder.stop()
                self.recording = False

    def detect(self):
        self.read_frame()
        self.process_frame()
        return (self.lock, self.deer_pos)
    
    def off(self):
        # stop capture and quit
        self.recorder.stop()
        mi48.stop()


class Recorder():
    def __init__(self):

        now = datetime.now()
        date_folder = now.strftime("/home/ohdeer/oh-deer/auto-tests/%Y-%m-%d_clips/")
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        self.filename = now.strftime("%H-%M-%S")
        self.fps = 15
        self.start_time = time.time()

        fourcc = cv.VideoWriter_fourcc(*'MJPG')  # Codec for .avi format
        # self.raw = cv.VideoWriter(f"{self.filename}_raw", fourcc, self.fps, (80, 62), isColor=False)
        # self.processed = cv.VideoWriter(f"{self.filename}_processed", fourcc, self.fps, (80, 62), isColor=False)
        self.bbox = cv.VideoWriter(f"{date_folder}{self.filename}_bbox.avi", fourcc, self.fps, (80, 62), isColor=False)

    def get_time(self):
        return time.time() - self.start_time
    
    def write_bbox(self, frame):
#        self.bbox.write(cv.rotate(frame, cv.ROTATE_90_CLOCKWISE))
         self.bbox.write(frame)

    def stop(self):
        self.bbox.release()
        print("Stop recording")
        del self
        
    def __del__(self):
        print("Delete recorder")


       

# Visualise data after reshaping the array properly
# img = data_to_frame(data, mi48.fpa_shape)
# try:
#     img = plt.imshow(img.astype(np.float32), cmap='coolwarm',
#                      aspect='equal', interpolation=None)
#     plt.axis('off')
#     plt.show()
# except NameError:
#     # plt not found/not imported/missing
#     pass
