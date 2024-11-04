"""
Working document to play around with image segmentation. 

Includes some of the notes and process stuff that would help change and develop it later on.
"""

import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np


# load and display image 
image_path = 'imgs/therm3_5ppl.jpg' #'imgs/therm1_person.JPG'
img = cv.imread(image_path)

# Convert from BGR (OpenCV's default) to RGB (Matplotlib's default)
img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
img_gray = cv.cvtColor(img_rgb, cv.COLOR_RGB2GRAY)

r, g, b= cv.split(img_rgb)
channels = [b, g, r]
img_blue = channels[0] # better for picking out the hottest parts with the white background color scheme

_, thresh = cv.threshold(img_gray, 100, 255, cv.THRESH_BINARY_INV) # thresh_binary_inv is important to pick out the dark part instead of the light part (depends on what color scheme you use)
# note that right now using the white background image it's looking at some of the darker parts of the heat spectrum (less hot) to
# identify the object. If we want to switch to the black background image, then it'll be easier to pull out the absolute hotteset part.

bounding = img_rgb.copy()
contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
c = []

# filter out contours that are too small
min_area = 100  # Adjust this value
for contour in contours:
    area = cv.contourArea(contour)
    if area > min_area:
        c.append(contour)
        pass

print(f' all contours: {len(contours)}')
print(f'filtered: {len(c)}')

for contour in c:
    # cv.drawContours(bounding, c,  -1, (0, 0, 255), 5)
    x, y, w, h = cv.boundingRect(contour)
    cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 2)  # draw box

# Display the result
plt.imshow(bounding)
plt.axis('off')
plt.show()