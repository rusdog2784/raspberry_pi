import numpy as np
import imutils
import cv2


class SingleMotionDetector:
    def __init__(self, accumulated_weight=0.5):
        self.accumulated_weight = accumulated_weight
        self.background = None
        
    def update(self, image):
        if self.background is None:
            self.background = image.copy().astype("float")
            return
        cv2.accumulateWeighted(image, self.background, self.accumulated_weight)
        
    def detect(self, image, t_val=25):
        delta = cv2.absdiff(self.background.astype("uint8"), image)
        thresh = cv2.threshold(delta, t_val, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        (min_x, min_y) = (np.inf, np.inf)
        (max_x, max_y) = (-np.inf, -np.inf)
        if len(contours) == 0:
            return None
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            (min_x, min_y) = (min(min_x, x), min(min_y, y))
            (max_x, max_y) = (max(max_x, x + w), max(max_y, y + h))
        return (thresh, (min_x, min_y, max_x, max_y))
    