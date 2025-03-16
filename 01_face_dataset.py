from picamera2 import Picamera2
import cv2
import os
import numpy as np

# Initialize the camera
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
cam.start()

face_detector = cv2.CascadeClassifier('/home/nhom1/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
cv2.startWindowThread()

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

while True:
    # Capture frame-by-frame
    frame = cam.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0))
        count += 1

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])
        cv2.imshow('image', frame)
        print(30 - count)

    k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
    if k == 27:
        print('User interrupted.')
        break
    elif count >= 30:  # Take 30 face samples and stop video
        print('Data collected!')
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.stop()
cv2.destroyAllWindows()
