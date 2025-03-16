import cv2
import numpy as np
from picamera2 import Picamera2
from flask import Flask, render_template, Response, request, jsonify
import threading
import os
from datetime import datetime, timedelta
import subprocess

app = Flask(__name__)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')  # load faces
cascadePath = "/home/nhom1/opencv/data/haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

names = ['None', 'HaiNam', 'Vu']
captured_faces = []
capturing = False

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))

def mark_attendance(name):
    result = subprocess.run(["./wiringpi", name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Attendance marked for {name}")

def capture_faces():
    global capturing
    camera.start()
    while True:
        frame = camera.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(30, 30),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            if confidence < 100:
                name = names[id]
                confidence_text = "  {0}%".format(round(100 - confidence))
            else:
                name = "unknown"
                confidence_text = "  {0}%".format(round(100 - confidence))

            cv2.putText(frame, str(name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(frame, str(confidence_text), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
            
            # Kiểm tra thời gian cập nhật gần nhất
            now = datetime.now()
            if not any(face[0] == id and now - face[2] < timedelta(seconds=20) for face in captured_faces):
                captured_faces.append((id, name, now))
                mark_attendance(name)
            
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    camera.stop()

@app.route('/video_feed')
def video_feed():
    return Response(capture_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html', captured_faces=captured_faces)

@app.route('/start', methods=['POST'])
def start_capture():
    global capturing
    capturing = True
    return 'Started capturing faces.'

@app.route('/stop', methods=['POST'])
def stop_capture():
    global capturing
    capturing = False
    return 'Stopped capturing faces.'

@app.route('/captured_faces')
def get_captured_faces():
    return jsonify(captured_faces=[{
        'id': face[0],
        'name': face[1],
        'time': face[2].strftime("%Y-%m-%d %H:%M:%S")
    } for face in captured_faces])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)