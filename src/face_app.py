from datetime import datetime

from database import db_utils
from face_recognition import face_analysis
import cv2
import mxnet as mx
import config
from src import embedding_utils

class face_app:
    def __init__(self):
        self.CAMERA_IDS = [0]
        self.CAMERA_OBJECTS = [cv2.VideoCapture(camera_id) for camera_id in self.CAMERA_IDS]

        #Load gallery data into memory
        embedding_utils.load_gallery()

    def run(self):
        # Gather all frames
        frames = []
        for camera in self.CAMERA_OBJECTS:
            ret, image = camera.read()
            frames.append(image if ret else None)

        frames_output = []
        for frame in frames:
            faces = face_analysis.get(img=frame, det_scale=config.DETECTION_SCALE)
            frames_output.append([frame, faces])
            for face in faces:
                result = embedding_utils.compare_with_enrolled_data(query=face.normed_embedding)



        #draw names and bbox on images
        for frame, output in frames_output:
            for face in output:
                x1,y1, x2, y2 = list(map(int, face.bbox.tolist()))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


        cv2.imshow('result', frames[0])
        cv2.waitKey(1)
        return frames[0]

    def add_person(self, img, name):
        status, result = db_utils.add_user(name=name,enrol_date=datetime.now())
        if not status:
            print(result)
        status = embedding_utils.add_person(id=result, img=img)
        if not status:
            db_utils.remove_user(result)
            print("Error : image not add in filesystem")

        print(f'{name} person successfully added')
        return True

    def remove_person(self, id):
        person_name = db_utils.get_person_details_from_id(id)[0]
        status, result = db_utils.remove_user(id=id)
        if not status:
            print(result)
        status = embedding_utils.remove_person(id=id)
        if not status:
            print("Error : image not removed from filesystem")

        print(f'{person_name} successfully removed')
        return True