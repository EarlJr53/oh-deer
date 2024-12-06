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
video_path = "11_17_test_vids/one_m_raw.mp4"

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
    

    # If the frame was not read successfully, end of video is reached
    if not ret:
        print("End of video.")
        break

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv_render(frame, title='raw',resize=(400,310), colormap = 'gray', interpolation=cv.INTER_CUBIC)

    dminav = RollingAverageFilter(N=10)
    dmaxav = RollingAverageFilter(N=10)

    min_temp = dminav(np.min(frame))  # + 1.5
    max_temp = dmaxav(np.max(frame))  # - 1.5
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
    cv_render(normalized_frame, title='norm frame',resize=(400,310), colormap='gray', interpolation=cv.INTER_CUBIC)
    
    # img = filt_uint8.astype(np.uint8)
    img = normalized_frame.astype(np.uint8)
    bounding = img.copy()

    # # image segmentation
    if not_noise:
        _,thresh = cv.threshold(img.astype(np.uint8),0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # print(f'all: {len(contours)}')
        c_filtered = [] # all contours within range
        c_min = [[0,0],[0,62],[80, 62],[80, 0],[0, 0]] # smallest contour

        # filter out contours that are too small
        min_area = 20  # Adjust this value
        max_area = 2300 # total area of frame is (hypothetically) 4960
        for contour in contours:
            area = cv.contourArea(contour)
            if area > min_area and area < max_area:
                c_filtered.append(contour)
                
                # if area < cv.contourArea(c_min):
                #     c_min = contour

        # print(f'filt: {len(c_filtered)}')
        
        if len(c_filtered) >= 1:
        #     contour = min([cv.contourArea(c) for c in c_filtered])
        #     print(f'contour picked: {contour}')

        # for contour in c_filtered:
            
        #     cv.drawContours(bounding, contour,  -1, (0, 0, 255), 5)
            contour = c_filtered[0]
            x, y, w, h = cv.boundingRect(contour)
            cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 1)  # draw box
            
            centroid_x = int(x + w/2) # horizontal centroid wrt pixels 0-80
            centroid_y = int(y + h/2) # verticle centroid
            print(f'centroid:{centroid_x}')
            cv.circle(bounding, (centroid_x, centroid_y), 3, (255, 0, 0), 2)
            print(f'contour - x:{x}, y:{y}, w:{w}, h:{h}')
            # print(f'area: {cv.contourArea(contour)}')
            # print('cycle done')
        else:
            pass

    # Display the processed frame
    # cv.imshow("Processed Frame", processed_frame)
    # cv.imshow("Processed Frame", frame, resize=(400,310))
    bounding.astype(np.uint8)
    cv_render(bounding, title='bbox',resize=(400,310), colormap = 'gray', interpolation=cv.INTER_CUBIC)

    # Press 'q' to exit the video playback
    if cv.waitKey(frame_delay) & 0xFF == ord('q'):
        break

# Release the video capture object and close display windows
cap.release()
cv.destroyAllWindows()
