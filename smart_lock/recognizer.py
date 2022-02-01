import cv2
import numpy as np
import pickle
import time
import os
import urllib
import datetime
from iot_project.settings import BASE_DIR


if os.path.getsize(str(BASE_DIR) +"/smart_lock/ML/face-labels.pkl") > 0:
    name={}
    labels = {"person_name": 1}
    with open(str(BASE_DIR) +"/smart_lock/ML/face-labels.pkl", 'rb') as f:
        og_labels = pickle.load(f)
        labels = {v:k for k,v in og_labels.items()}


class FaceRecognizer(object):
    def __init__(self):
        #self.url = "http://192.168.43.77:8080/shot.jpg"
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        #cv2.destroyAllWindows()
        self.video.release()
    
    def recognizer(self):
        success, img = self.video.read()
        frame_flip = cv2.flip(img, 1)
        face_cascade = cv2.CascadeClassifier(str(BASE_DIR) + "/smart_lock/ML/data/haarcascade_frontalface_default.xml")
        if os.path.getsize(str(BASE_DIR) +"/smart_lock/ML/face-trainner.yml") > 0:
            nn = cv2.face.LBPHFaceRecognizer_create()
            nn.read(str(BASE_DIR) +"/smart_lock/ML/face-trainner.yml")
        #imgResp = urllib.request.urlopen(self.url)
        #imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        #img = cv2.imdecode(imgNp, -1)
        frame_flip = cv2.flip(img, 1)
        gray = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame_flip[y:y + h, x:x + w]

            if os.path.getsize(str(BASE_DIR) +"/smart_lock/ML/face-trainner.yml") > 0:
                id_, conf = nn.predict(roi_gray)
                if conf >= 4 and conf <= 85:
                    frame_flip = cv2.putText(frame_flip, labels[id_]+'('+str(round(conf,4))+')', (x-10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,255,102), 2, cv2.LINE_AA)
                if labels[id_] in name.keys():
                    name[labels[id_]]+=1
                else:
                    name[labels[id_]] = 0
            frame_flip = cv2.rectangle(frame_flip, (x, y), (x+w,y+h), (255,0,0), 3)

        date_time = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        font = cv2.FONT_HERSHEY_SIMPLEX
        frame_flip = cv2.putText(frame_flip, date_time, (5, 40), font, 0.7, (0, 255, 255), 1, cv2.LINE_AA)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()
