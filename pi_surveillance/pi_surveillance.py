import argparse
import warnings
import imutils
#import dropbox
import logging
import json
import time
import cv2

from datetime import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
#from pyimagesearch.tempimage import TempImage
from logger import setup_custom_logger


#####################################################################################


# Construct the argument parser and parse the arguments.
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="path to the configuration file")
args = vars(ap.parse_args())


# Initialize the logger.
logger = setup_custom_logger("main", "logs")


# Filter warnings, load the configuration and initialize the <EXTERNAL FILE STORAGE>.
warnings.filterwarnings("ignore")
conf = json.load(open(args['conf']))
client = None
if conf['use_dropbox']:
    client = dropbox.Dropbox(conf['dropbox_access_token'])
    logger.info("SUCCES - dropbox account linked")


# Initialize the camera and grab a reference to the raw camera capture.
camera = PiCamera()
camera.resolution = tuple(conf['resolution'])
camera.framerate = conf['fps']
raw_capture = PiRGBArray(camera, size=tuple(conf['resolution']))


# Allow the camera to warmup, then initialize the average frame, last uploaded timestamp,
# and frame motion counter.
logger.info("warming up...")
time.sleep(conf['camera_warmup_time'])
avg = None
last_uploaded = datetime.utcnow()
motion_counter = 0


# Capture frames from the camera
for f in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    frame = f.array
    timestamp = datetime.utcnow()
    text = "Unoccupied"
    
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if avg is None:
        logger.info("starting background model...")
        avg = gray.copy().astype("float")
        raw_capture.truncate(0)
        continue
    
    cv2.accumulateWeighted(gray, avg, 0.5)
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    
    thresh = cv2.threshold(frame_delta, conf['delta_threshold'], 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    
    for c in contours:
        if cv2.contourArea(c) < conf['min_area']:
            continue
        
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        text = "Occupied"
        
    timestamp_string = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, f"Room Status: {text}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, timestamp_string, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    
    if text == "Occupied":
        if (timestamp - last_uploaded).seconds >= conf['min_upload_seconds']:
            motion_counter += 1
            
            if motion_counter >= conf['min_motion_frames']:
                if conf['use_dropbox']:
                    t = TempImage()
                    cv2.imwrite(t.path, frame)
                    logger.info(f"uploading image ({timestamp_string})")
                    path = f"/{conf['dropbox_base_path']}/{timestamp_string}.jpg"
                    client.files_upload(open(t.path, "rb").read(), path)
                    t.cleanup()
                
                last_uploaded = timestamp
                motion_counter = 0
    else:
        motion_counter = 0
        
    if conf['show_video']:
        cv2.imshow("Security Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
    raw_capture.truncate(0)
            



