# import the necessary packages
from flask import Flask, render_template, Response
from camera2 import VideoCamera
import cv2
import webbrowser
import camera2
#import keyboard
webbrowser.open('http://127.0.0.1:5000/')
app = Flask(__name__)
@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')
def gen(camera):
    while True:
        #get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        key = cv2.waitKey(1) & 0xFF
 
   
        if key == ord("q"):
            break
 
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__ == '__main__':
    # defining server ip address and port
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=False)
