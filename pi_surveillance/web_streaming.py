from pyimagesearch.motion_detection.single_motion_detector import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response, Flask, render_template
from datetime import datetime
from pathlib import Path
import threading
import argparse
import imutils
import time
import cv2


output_frame = None
lock = threading.Lock()


app = Flask(__name__)


vs = VideoStream(src=0).start()
time.sleep(2.0)
motion_detected = False
motion_counter = 0
last_uploaded = datetime.utcnow()
min_upload_seconds = 3.0
min_motion_frames = 10


saved_image_path = Path("/tmp/home_surveillance")
saved_image_path.mkdir(parents=True, exist_ok=True)
print(f"Created temporary directory: {saved_image_path}")


def detect_motion(frame_count):
    global vs, output_frame, lock, motion_detected, motion_counter, last_uploaded
    md = SingleMotionDetector(accumulated_weight=0.1)
    total = 0
    detections = 0
    
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        
        timestamp = datetime.utcnow()
        timestamp_string = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, timestamp_string, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        
        if total > frame_count:
            motion = md.detect(gray)
            if motion is not None:
                (thresh, (min_x, min_y, max_x, max_y)) = motion
                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
                if (timestamp - last_uploaded).seconds >= min_upload_seconds:
                    motion_counter += 1
                    if motion_counter >= min_motion_frames:
                        #motion_detected = True
                        timestamp_string = datetime.utcnow().strftime("%H%M%S%f")[:-3]
                        image_file = str(Path(saved_image_path, f"{timestamp_string}.jpg"))
                        cv2.imwrite(image_file, frame)
                        print(f"MOTION DETECTED! Saved file: {image_file}")                        
                        last_uploaded = timestamp
                        motion_counter = 0
            else:
                #motion_detected = False
                motion_counter = 0
                
        md.update(gray)
        total += 1
        
        with lock:
            output_frame = frame.copy()
            

def generate():
    global output_frame, lock
    
    while True:
        with lock:
            if output_frame is None:
                continue
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')
            
            
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32, help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    
    t = threading.Thread(target=detect_motion, args=(args['frame_count'],))
    t.daemon = True
    t.start()
    
    app.run(host=args['ip'], port=args['port'], debug=True, threaded=True, use_reloader=False)
    

vs.stop()



