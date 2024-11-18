import cv2 as cv
import sys
sys.path.append("/home/test/myenv/lib/python3.11/site-packages")
import os
import signal
import time
import logging
import serial
import numpy as np

# Path to the video file
video_path = "/home/igoyal/RoboSys/oh-deer/test1_raw.mp4"

# Open the video file
cap = cv.VideoCapture(video_path)
frame_delay = int(1000 / 15) #15 is the current fps, adjust as necessary

# Check if the video was successfully opened
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

from senxor.utils import data_to_frame, remap, cv_filter,\
                         cv_render, RollingAverageFilter,\
                         connect_senxor

par = {'blur_ks':3, 'd':5, 'sigmaColor': 27, 'sigmaSpace': 27}

# Loop through each frame of the video
while True:
    # Read the next frame
    ret, frame = cap.read()
    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #.astype(np.uint8)
    # print(frame.shape)
    

    # If the frame was not read successfully, end of video is reached
    if not ret:
        print("End of video.")
        break

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    print(frame.shape)

    dminav = RollingAverageFilter(N=10)
    dmaxav = RollingAverageFilter(N=10)

    min_temp = dminav(frame.min())  # + 1.5
    max_temp = dmaxav(frame.max())  # - 1.5
    # frame = data_to_frame(frame, hflip=False)
    # don't create bounding boxes when there is not much temp variation in the frame (assume it is noise)
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
    # normalized_frame = ((filt_uint8 - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)
    
    # img = filt_uint8.astype(np.uint8)
    img = normalized_frame.astype(np.uint8)
    bounding = img.copy()

    # # image segmentation
    if not_noise:
        _,thresh = cv.threshold(img.astype(np.uint8),0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
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


    # Display the processed frame
    # cv.imshow("Processed Frame", processed_frame)
    # cv.imshow("Processed Frame", frame, resize=(400,310))
    bounding.astype(np.uint8)
    cv_render(bounding, title='frame',resize=(400,310), colormap='gray', interpolation=cv.INTER_CUBIC)

    # Press 'q' to exit the video playback
    if cv.waitKey(frame_delay) & 0xFF == ord('q'):
        break

# Release the video capture object and close display windows
cap.release()
cv.destroyAllWindows()
