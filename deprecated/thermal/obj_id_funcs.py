import cv2 as cv
from matplotlib import pyplot as plt

def find_bboxes(image_path):

    """
    Outputs bounding boxes for all living objects in a thermal image.

    Args:
        image_path (str): path to input image

    Returns 
        array: array of bounding boxes, where each list inside array is in format [x, y, w, h]

    """
    img = cv.imread(image_path)

    # Convert from BGR (OpenCV's default) to RGB (Matplotlib's default)
    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_RGB2GRAY)

    _, thresh = cv.threshold(img_gray, 100, 255, cv.THRESH_BINARY_INV) # Picks out the dark parts of the image

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

    output = []

    for contour in c:
        x, y, w, h = cv.boundingRect(contour) # determine rectangular bounding box
        output.append([x, y, w, h]) # add the rectangle to the output array
    
    return output
    

def disp_bboxes(bboxes):

    img = cv.imread(image_path).copy()

    for box in bboxes:
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]

        cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    plt.imshow(img)
    plt.axis('off')
    plt.show()

image_path = 'imgs/therm2_2ppl.jpg'
bboxes = find_bboxes(image_path)
disp_bboxes(bboxes)