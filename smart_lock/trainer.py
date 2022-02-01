import cv2
import os
import numpy as np
from PIL import Image
import pickle
import shutil
from iot_project.settings import BASE_DIR


current_id = 0
label_ids = {}
y_labels = []
x_train = []


class FaceTrainer(object):
    def __init__(self):
        self.img_dir = os.path.join(BASE_DIR, 'smart_lock/ML/dataset')

    def trainer(self):
        global current_id
        face_cascade = cv2.CascadeClassifier(str(BASE_DIR) + "/smart_lock/ML/data/haarcascade_frontalface_default.xml")
        nn = cv2.face.LBPHFaceRecognizer_create()
        for root, dirs, files in os.walk(self.img_dir):
            for file in files:
                if file.endswith('jpg') or file.endswith('jpeg'):
                    path = os.path.join(root, file)
                    label = os.path.basename(os.path.dirname(path))
                    # print(label_ids)
                    if not label in label_ids:
                        label_ids[label] = current_id
                        current_id = current_id + 1
                    id_ = label_ids[label]
                    pil_img = Image.open(path).convert("L")
                    img_array = np.array(pil_img, "uint8")
                    faces = face_cascade.detectMultiScale(img_array, scaleFactor=1.5, minNeighbors=5)
                    # fetch the ROI from imgs
                    for (x, y, w, h) in faces:
                        roi = img_array[y:y + h, x:x + w]
                        x_train.append(roi)
                        y_labels.append(id_)

        with open(str(BASE_DIR) + "/smart_lock/ML/face-labels.pkl", 'wb') as f:
            pickle.dump(label_ids, f)
        nn.train(x_train, np.array(y_labels))
        nn.save(str(BASE_DIR) + "/smart_lock/ML/face-trainner.yml")

    def del_data(self):
        for root, dirs, files in os.walk(self.img_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))