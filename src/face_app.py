from datetime import datetime

import cv2
import numpy as np
import config
from database import db_utils
from face_recognition import face_analysis
from src import embedding_utils, utils


class Face_app:
    def __init__(self, queue=None):
        # Database initialization
        db_utils.init_database()

        self.CAMERA_IDS, self.CAMERA_OBJECTS = [], []
        _, camera_paths = db_utils.get_active_camera_list()
        for c_id, camera_path in camera_paths:
            cap_status, cap_result = self.get_camera_object(camera_path)
            if not cap_status:
                print(f'Error: camera: {camera_path}, {cap_result}')

            print(f"Cam initialized : {camera_path}")
            self.CAMERA_OBJECTS.append(cap_result)


        # Load gallery data into memory
        embedding_utils.load_gallery()

        # queue for perform operation in running server
        self.queue = queue

        cv2.namedWindow('result', cv2.WINDOW_NORMAL)

    def run(self):
        try:
            # Process queued operation
            self.processed_queued_functions()
        except Exception as e:
            print(e)

        # Gather all frames
        frames = []
        for camera in self.CAMERA_OBJECTS:
            ret, image = camera.read()
            frames.append(image if ret else None)

        frames_output = []
        for frame in frames:
            if frame is None:
                frames_output.append([frame, []])
                continue
            faces = face_analysis.get(img=frame, det_scale=config.DETECTION_SCALE)
            frames_output.append([frame, faces])
            for face in faces:
                result = embedding_utils.compare_with_enrolled_data(query=face.normed_embedding)
                #TODO: store entry

        # draw names and bbox on images
        for frame, output in frames_output:
            for face in output:
                x1, y1, x2, y2 = list(map(int, face.bbox.tolist()))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        combined_image = utils.generate_combine_image(frames)

        cv2.imshow('result', combined_image)
        cv2.waitKey(1)
        return combined_image

    def processed_queued_functions(self):
        if self.queue is None:
            return
        while self.queue.qsize():
            data = self.queue.get(timeout=3)
            fun_name, kargs = data.items()
            function = self.__getattribute__(fun_name)
            function(**kargs)

    def add_person(self, img, name):
        status, result = db_utils.add_user(name=name, enrol_date=datetime.now())
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

    def add_camera(self, camera_path):
        status, camera_id = db_utils.add_camera(camera_path=camera_path)
        if status:
            cap_status, cap_result = self.get_camera_object(camera_path)
            if not cap_status:
                print(f'Error: camera: {camera_path}, {cap_result}')
            self.CAMERA_OBJECTS.append(cap_result)

    def get_camera_object(self, camera_path):
        try:
            if str(camera_path).isnumeric():
                camera_path = int(camera_path)
            cap = cv2.VideoCapture(camera_path)
            return True, cap
        except Exception as e:
            return False, e
