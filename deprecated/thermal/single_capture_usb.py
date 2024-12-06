# Copyright (C) Meridian Innovation Ltd. Hong Kong, 2019. All rights reserved.
#
import os
import time
import numpy as np
import logging
import serial
import cv2 as cv

try:
    import matplotlib
    from matplotlib import pyplot as plt
except:
    print("Please install matplotlib to see the thermal image")

from senxor.mi48 import MI48, format_header, format_framestats
from senxor.utils import data_to_frame, connect_senxor

# This will enable mi48 logging debug messages
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

mi48, connected_port, port_names = connect_senxor()

# print out camera info
logger.info('Camera info:')
logger.info(mi48.camera_info)

# initiate single frame acquisition
with_header = True
mi48.start(stream=False, with_header=with_header)

# Read the frame
data, header = mi48.read()
# Log the header and frame stats
if header is not None:
    logger.debug('  '.join([format_header(header),
                            format_framestats(data)]))
else:
    logger.debug(format_framestats(data))

# Visualise data after reshaping the array properly
img = data_to_frame(data, mi48.fpa_shape)
img = img.astype(np.uint8)

_,thresh = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
bounding = img.copy()
contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
c_filtered = []

# # filter out contours that are too small
min_area = 10  # Adjust this value
for contour in contours:
    area = cv.contourArea(contour)
    if area > min_area:
        c_filtered.append(contour)

print(f"\n length: {[cv.contourArea(c) for c in c_filtered]} \n")


for contour in c_filtered:
    # cv.drawContours(bounding, contour,  -1, (0, 0, 255), 5)
    x, y, w, h = cv.boundingRect(contour)
    cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 1)  # draw box

plt.imshow(img, cmap='gray',
                     aspect='equal', interpolation=None)
plt.axis('off')
plt.show()


plt.imshow(thresh, cmap='gray',
                    aspect='equal', interpolation=None)
plt.axis('off')
plt.show()

plt.imshow(bounding, cmap = 'gray',
                    aspect='equal', interpolation=None)
plt.axis('off')
plt.show()


# stop capture and quit
mi48.stop()
