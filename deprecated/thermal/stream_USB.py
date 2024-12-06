# Copyright (C) Meridian Innovation Ltd. Hong Kong, 2020. All rights reserved.
#
import sys
sys.path.append("/home/test/myenv/lib/python3.11/site-packages")
import os
import signal
import time
import logging
import serial
import numpy as np

try:
    import cv2 as cv
    import matplotlib
except:
    print("Please install OpenCV"
          " to see the thermal image")
    exit(1)

from senxor.mi48 import MI48, format_header, format_framestats
from senxor.utils import data_to_frame, remap, cv_filter,\
                         cv_render, RollingAverageFilter,\
                         connect_senxor

# video recordings
record = False
output_file_raw = ''
output_file_processed = ''
output_file_bbox = ''

# other settings
fps = 15

# This will enable mi48 logging debug messages
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

# Make the a global variable and use it as an instance of the mi48.
# This allows it to be used directly in a signal_handler.
global mi48

# define a signal handler to ensure clean closure upon CTRL+C
# or kill from terminal
def signal_handler(sig, frame):
    """Ensure clean exit in case of SIGINT or SIGTERM"""
    logger.info("Exiting due to SIGINT or SIGTERM")
    mi48.stop()
    cv.destroyAllWindows()
    logger.info("Done.")
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
logger.info('Camera info:')
logger.info(mi48.camera_info)

# set desired FPS
if len(sys.argv) == 2:
    STREAM_FPS = int(sys.argv[1])
else:
    STREAM_FPS = fps
mi48.set_fps(STREAM_FPS)

# see if filtering is available in MI48 and set it up
mi48.disable_filter(f1=True, f2=True, f3=True)
mi48.set_filter_1(85)
mi48.enable_filter(f1=True, f2=False, f3=False, f3_ks_5=False)
mi48.set_offset_corr(0.0)

mi48.set_sens_factor(100)
mi48.get_sens_factor()

# initiate continuous frame acquisition
with_header = True
mi48.start(stream=True, with_header=with_header)

# change this to false if not interested in the image
GUI = True

# set cv_filter parameters
par = {'blur_ks':3, 'd':5, 'sigmaColor': 27, 'sigmaSpace': 27}

dminav = RollingAverageFilter(N=10)
dmaxav = RollingAverageFilter(N=10)

# create VideoWriter
if record:
    fourcc = cv.VideoWriter_fourcc(*'MP4V')  # Codec for .avi format
    out_raw = cv.VideoWriter(output_file_raw, fourcc, fps, (80, 62), isColor=False)
    out_processed = cv.VideoWriter(output_file_processed, fourcc, fps, (80, 62), isColor=False)
    out_bbox = cv.VideoWriter(output_file_bbox, fourcc, fps, (80, 62), isColor=False)

while True:
    data, header = mi48.read()
    if data is None:
        logger.critical('NONE data received instead of GFRA')
        mi48.stop()
        sys.exit(1)

    # normalizes colors based on the min and max temp of the frame
    min_temp = dminav(data.min())  # + 1.5
    max_temp = dmaxav(data.max())  # - 1.5
    frame = data_to_frame(data, (80,62), hflip=False)
    raw = frame.astype(np.uint8)
    print(f'raw -  min:{np.min(raw)}, max:{np.max(raw)}')

    if record:
        out_raw.write(raw.astype(np.uint8))
    # don't create bounding boxes when there is not much temp variation in the frame (assume it is noise)
    not_noise = True
    # if data.max() - data.min() < 10: # note: adjust this value to change threshold for noise
    #     not_noise = False 

    # clip bottom values if the difference is too high
    if max_temp - min_temp > 20:
        min_temp = max_temp - 20

    frame = np.clip(frame, min_temp, max_temp)
    filt_uint8 = cv_filter(remap(frame), par, use_median=True,
                           use_bilat=True, use_nlm=False)
    
    normalized_frame = ((frame - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)
    # normalized_frame = ((filt_uint8 - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)
    
    # img = filt_uint8.astype(np.uint8)
    img = normalized_frame.astype(np.uint8)
    bounding = img.copy()
    print(f'normalized -  min:{np.min(img)}, max:{np.max(img)}')

    # image segmentation
    if not_noise:
        _,thresh = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        c_filtered = []

        # filter out contours that are too small
        min_area = 20  # Adjust this value
        for contour in contours:
            area = cv.contourArea(contour)
            if area > min_area:
                c_filtered.append(contour)

        for contour in c_filtered:
        # cv.drawContours(bounding, contour,  -1, (0, 0, 255), 5)
            x, y, w, h = cv.boundingRect(contour)
            cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 1)  # draw box
        

    if record:
        out_processed.write(normalized_frame)
        out_bbox.write(bounding)
    
    # uncomment to show min, max, avg, std
    # if header is not None:
    #     logger.debug('  '.join([format_header(header),
    #                             format_framestats(data)]))
    # else:
    #     logger.debug(format_framestats(data))

    if GUI:
        cv_render(raw, title='raw', resize=(400,310), colormap='gray')
        cv_render(filt_uint8, title='filtered', resize=(400,310), colormap='gray')
        cv_render(normalized_frame, title='processed', resize=(400,310), colormap='gray')
        cv_render(bounding, title='bounding', resize=(400,310), colormap='gray')
        # cv_render(thresh, title='binarized', resize=(400,310), colormap='gray')
        key = cv.waitKey(1)  # & 0xFF
        if key == ord("q"):
            break
#    time.sleep(1)

# stop capture and quit
out_raw.release()
out_bbox.release()
mi48.stop()
cv.destroyAllWindows()