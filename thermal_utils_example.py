import sys
sys.path.append("/home/ohdeer/venv/lib/python3.11/site-packages")
import os
import signal
import time
import logging
import serial
import numpy as np
import cv2 as cv

from senxor.mi48 import MI48, format_header, format_framestats
from senxor.utils import data_to_frame, remap, cv_filter,\
                         cv_render, RollingAverageFilter,\
                         connect_senxor

# This will enable mi48 logging debug messages
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

mi48, connected_port, port_names = connect_senxor()

# print out camera info
logger.info('Camera info:')
logger.info(mi48.camera_info)


class Thermal():
    def __init__(self):
        # initiate single frame acquisition
        with_header = True
        mi48.start(stream=False, with_header=with_header)

        self.frame
        self.deer_pos = -1
        self.lock = False

    def read_frame(self):
        # Read the frame
        data, header = mi48.read()
        # Log the header and frame stats
        if header is not None:
            logger.debug('  '.join([format_header(header),
                                    format_framestats(data)]))
        else:
            logger.debug(format_framestats(data))
        
        self.frame = data
    
    def process_frame(self):
        self.frame

        # add code here to segment and detect all potential deer in image

        if 0:       # if there are no deer present
            self.deer_pos = -1
            self.lock = False

        elif 1:     # if there is a single detected deer
            self.deer_pos = 40 # set self.deer_pos to the horizontal pixel of the deer to target
            self.lock = True

        elif 2:     # if there are multiple distinct deer present
            # add code here to choose which deer if multiple (maybe call a separate method?)
            self.deer_pos = 60
            self.lock = True

    def detect(self):
        self.read_frame()
        self.process_frame()
        return (self.lock, self.deer_pos)
    
    def off(self):
        # stop capture and quit
        mi48.stop()
       

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