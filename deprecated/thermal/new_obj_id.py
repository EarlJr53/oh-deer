import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np


# load and display image 
image_path = '/home/igoyal/RoboSys/oh-deer/imgs/single_capture_1.png' 
img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)

# apply otsu binary map 
# note to self: makes fairly good binarized version, though the low resolution could be an issue
ret2,thresh = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# plt.imshow(thresh, cmap='gray')
# plt.show()


# _, thresh = cv.threshold(img, 100, 255, cv.THRESH_BINARY) # thresh_binary_inv is important to pick out the dark part instead of the light part (depends on what color scheme you use)
# # note that right now using the white background image it's lookqqing at some of the darker parts of the heat spectrum (less hot) to
# # identify the object. If we want to switch to the black background image, then it'll be easier to pull out the absolute hotteset part.

bounding = img.copy()
contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
print(contours)
# c = []

# # filter out contours that are too small
# min_area = 100  # Adjust this value
# for contour in contours:
#     area = cv.contourArea(contour)
#     if area > min_area:
#         c.append(contour)
#         pass

for contour in contours:
    cv.drawContours(bounding, contour,  -1, (0, 0, 255), 5)
    # x, y, w, h = cv.boundingRect(contour)
    x, y, w, h = [200, 200, 50, 50]
    cv.rectangle(bounding, (x, y), (x + w, y + h), (255, 0, 0), 2)  # draw box

plt.imshow(img, cmap = 'gray')
# plt.axis('off')
plt.show()