from scipy.spatial import distance as dist
from gaze_tracking import GazeTracking
from imutils.video import VideoStream
from imutils import face_utils
from imutils.video import FPS
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2
# defining face detector

def sound_alarm(path):
    # play an alarm sound
        playsound.playsound(path)

def eye_aspect_ratio(mouth):
        M = dist.euclidean(mouth[2], mouth[10])
        N = dist.euclidean(mouth[4], mouth[8])
        K = dist.euclidean(mouth[0], mouth[6])
        mar = (M + N) / (2.0 * K)
        return mar
gaze = GazeTracking()
ala = "alaram.wav"
EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.42
EYE_AR_CONSEC_FRAMES = 48
ALARM_ON = False
face_cascade = cv2.CascadeClassifier('face.xml')
font = cv2.FONT_HERSHEY_SIMPLEX

if face_cascade.empty():
    raise IOError('Unable to load the face cascade classifier xml file')
s=0
scaling_factor = 0.75
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
#predictor = dlib.shape_predictor(args["shape_predictor"])

predictor = dlib.shape_predictor("shape.dat")
# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart1, lEnd1) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
#(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
#vs = VideoStream(src=args["webcam"]).start()
#vs = cv2.VideoCapture(0)

class VideoCamera(object):
    def __init__(self):
       #capturing video
       self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        #releasing camera
        
        self.video.release()
    
 
    def get_frame(self):
       #extracting frames
       ret, frame = self.video.read()
       #frame = imutils.resize(frame, width=450)
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       width  = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))   # float
       height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
       gaze.refresh(frame)
       frame = gaze.annotated_frame()
       text = ""
       # detect faces in the grayscale frame
       rects = detector(gray, 0)
       face_rects = face_cascade.detectMultiScale(gray, 1.2, 5) 
       if len(face_rects)== 0:
            cv2.putText(frame, "Student is not present", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.line(frame,(0,0),(width,0),(0,0,255),9)
            cv2.line(frame,(0,0),(0,height),(0,0,255),9)
            cv2.line(frame,(0,height),(width,height),(0,0,255),9)
            cv2.line(frame,(width,0),(width,height),(0,0,255),9)
       if len(face_rects)>1:
            cv2.putText(frame, "More than 1 people found", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.line(frame,(0,0),(width,0),(0,0,255),9)
            cv2.line(frame,(0,0),(0,height),(0,0,255),9)
            cv2.line(frame,(0,height),(width,height),(0,0,255),9)
            cv2.line(frame,(width,0),(width,height),(0,0,255),9)
       for (x,y,w,h) in face_rects:
           cv2.rectangle(frame, (x,y), (x+w,y+h), (1000,255,23430), 2)

       cv2.rectangle(frame, ((0,frame.shape[0] -25)),(270, frame.shape[0]), (255,255,255), -1)
       cv2.putText(frame, "Number of faces detected: " + str(len(face_rects)), (0,frame.shape[0] -10), cv2.FONT_HERSHEY_TRIPLEX, 0.5,  (0,0,0), 1)	
    
       # loop over the face detections
       for rect in rects:
        
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        
        mouth = shape[lStart1:lEnd1]
        
        MAR = eye_aspect_ratio(mouth)
        
        mouthHull = cv2.convexHull(mouth)
        #rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
        
        if MAR > MOUTH_AR_THRESH:
            #COUNTER += 1
            cv2.putText(frame, "Lips movement ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.line(frame,(0,0),(width,0),(0,0,255),9)
            cv2.line(frame,(0,0),(0,height),(0,0,255),9)
            cv2.line(frame,(0,height),(width,height),(0,0,255),9)
            cv2.line(frame,(width,0),(width,height),(0,0,255),9)
       if gaze.is_right():
        text = "Looking right"
        cv2.line(frame,(0,0),(width,0),(0,0,255),9)
        cv2.line(frame,(0,0),(0,height),(0,0,255),9)
        cv2.line(frame,(0,height),(width,height),(0,0,255),9)
        cv2.line(frame,(width,0),(width,height),(0,0,255),9)
        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
       elif gaze.is_left():
        text = "Looking left"
        cv2.line(frame,(0,0),(width,0),(0,0,255),9)
        cv2.line(frame,(0,0),(0,height),(0,0,255),9)
        cv2.line(frame,(0,height),(width,height),(0,0,255),9)
        cv2.line(frame,(width,0),(width,height),(0,0,255),9)
        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
      
       left_pupil = gaze.pupil_left_coords()
       right_pupil = gaze.pupil_right_coords()
       coord = gaze.horizontal_ratio()   
        #cv2.putText(frame, "MAR: {:.2f}".format(MAR), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # encode OpenCV raw frame to jpg and displaying it
       ret, jpeg = cv2.imencode('.jpg', frame)
       return jpeg.tobytes()
