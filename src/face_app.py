import os
import time
from copy import deepcopy
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

        self.CAMERA_OBJECTS = []
        self.update_camera_objects()

        # Load gallery data into memory
        embedding_utils.load_gallery()

        # queue for perform operation in running server
        self.queue = queue

        self.recent_entries = {}
        # cv2.namedWindow('result', cv2.WINDOW_NORMAL)

    def run(self):
        try:
            # Process queued operation
            self.processed_queued_functions()
        except Exception as e:
            print(e)

        # Gather all frames
        frames = []
        for camera_id, camera in self.CAMERA_OBJECTS:
            ret, image = camera.read()
            frames.append((camera_id, image if ret else None))

        frames_output = []
        for camera_id, frame in frames:
            if frame is None:
                frames_output.append([frame, []])
                continue
            faces = face_analysis.get(img=frame, det_scale=config.DETECTION_SCALE)
            frames_output.append([frame, faces])
            for face in faces:
                x1, y1, x2, y2 = list(map(lambda x: 0 if x < 0 else int(x), face.bbox.tolist()))

                result = embedding_utils.compare_with_enrolled_data(query=face.normed_embedding)
                matched_id, dist = result

                if dist > config.UNKNOWN_THRES:
                    matched_id = 'unknown'

                if not self.is_entry_recent(name=matched_id, embedding=face.normed_embedding):
                    self.add_entry(name=matched_id, face_crop=deepcopy(frame[y1:y2, x1:x2]))

                if config.VISUALIZE:
                    # draw names and bbox on images
                    text_dict = {'id': 'Unknown'}
                    if matched_id != 'unknown':
                        person_data = embedding_utils.get_id_metadata(id=matched_id)
                        text_dict = {'id': person_data[0], 'name': person_data[1], 'company_id': person_data[4],
                                     'grade': person_data[5], 'extra': person_data[6]}
                    frame = utils.set_text_with_box(text_dict=text_dict, background=frame, x=x2, y=y1,
                                                    box_h_w=[y2 - y1, 150])

                    x1, y1, x2, y2 = list(map(int, face.bbox.tolist()))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (150, 150, 150), 2)

        # combined_image = None
        # if frames:
        #     combined_image = utils.generate_combine_image(frames, image_size=(1280, 1000))
        # cv2.imshow('result', combined_image)
        # cv2.waitKey(1)

        return frames

    def processed_queued_functions(self):
        if self.queue is None:
            return

        while self.queue.qsize() > 0:
            data = self.queue.get(timeout=3)
            fun_name, kargs = list(data.items())[0]
            function = self.__getattribute__(fun_name)
            function(**kargs)

    def add_entry(self, face_crop, name):
        status, entry_id = db_utils.add_entry(name=name, time=datetime.now())
        if not status:
            print(f'Recognition entry not update in database')
            return False

        img_name = str(entry_id) + '.png'
        embedding_utils.save_entry_image(face_crop=face_crop, img_name=img_name)
        return True

    def add_person(self, img, name, company_id='', grade='', extra=''):
        faces = face_analysis.get(img=img, det_scale=0.5)
        if not faces:
            print(f'No Face detected in image')
            return False
        matched_name, dist = embedding_utils.compare_with_enrolled_data(query=faces[0].normed_embedding)
        if dist <= config.UNKNOWN_THRES:
            print(f'Person already enrolled with different id {matched_name}')
            return False

        status, result = db_utils.add_person(name=name, enrol_date=datetime.now(), company_id=company_id, grade=grade,
                                             extra=extra)
        if not status:
            print(result)
            return False

        status, person_data = db_utils.get_person_details_from_id(result)
        status = embedding_utils.add_person(id=result, img=img, metadata=person_data)
        if not status:
            db_utils.remove_user(result)
            print("Error : image not add in filesystem")
            return False

        print(f'{name} person successfully added')
        return True

    def remove_person(self, id):
        person_name = db_utils.get_person_details_from_id(id)[1]
        status, result = db_utils.remove_user(id=id)
        if not status:
            print(result)
            return False
        status = embedding_utils.remove_person(id=id)
        if not status:
            print("Error : image not removed from filesystem")
            return False

        print(f'{person_name} successfully removed')
        return True

    def update_person(self, entry_id):
        status, result = db_utils.search_entry(id=entry_id)
        if not status:
            print(result)
            return False

        e_id, e_name, e_time = result[0]  # e_name==user.id
        status, _ = db_utils.get_person_details_from_id(e_name)
        if not status:
            print(f'User not found for id {e_name}')
            return False

        img_path = os.path.join(config.PROCESSED_DATA_PATH, str(e_id) + '.png')
        if not os.path.exists(img_path):
            print(f'entry image not exist')
            return False

        image = cv2.imread(img_path)
        status = embedding_utils.add_person(id=e_name, img=image)
        if not status:
            print("Error : image not add in filesystem")
            return False

        print(f'{e_name} person successfully added')
        return True

    def add_camera(self, camera_path):
        cap_status, cap_result = self.get_camera_object(camera_path)
        if not cap_status:
            print(f'Error: camera: {camera_path}, {cap_result}')
            return
        status, camera_id = db_utils.add_camera(camera_path=camera_path)
        if status:
            print(f'Camera :{camera_path} added')
            self.CAMERA_OBJECTS.append((camera_id, cap_result))

    def update_camera_objects(self):
        self.CAMERA_OBJECTS = []
        _, camera_paths = db_utils.get_active_camera_list()
        for camera_row in camera_paths:
            c_id, camera_path = camera_row[:2]
            cap_status, cap_result = self.get_camera_object(camera_path)
            if not cap_status:
                print(f'Error: camera: {camera_path}, {cap_result}')

            print(f"Cam initialized : {camera_path}")
            self.CAMERA_OBJECTS.append((c_id, cap_result))

    def get_camera_object(self, camera_path):
        try:
            if str(camera_path).isnumeric():
                camera_path = int(camera_path)
            cap = cv2.VideoCapture(camera_path)
            return True, cap
        except Exception as e:
            return False, e

    def is_entry_recent(self, name, embedding, timeframe=30):
        ct = time.time()
        if name.lower() != 'unknown':
            if name not in self.recent_entries:
                self.recent_entries[name] = ct
                return False

            previous_ct = self.recent_entries[name]
            if ct - previous_ct > timeframe:
                self.recent_entries[name] = ct
                return False
            else:
                return True
        else:
            self.recent_entries.setdefault('unknown', {})
            is_matched_unknown = False

            for previous_ct in list(self.recent_entries['unknown'].keys()):
                p_embedding = self.recent_entries['unknown'][previous_ct]
                if ct - previous_ct > 60 * 5:  # half hour
                    del self.recent_entries['unknown'][previous_ct]
                    continue

                distance = np.linalg.norm(p_embedding - embedding)
                if distance < config.UNKNOWN_THRES:
                    is_matched_unknown = True

            if not is_matched_unknown:
                self.recent_entries['unknown'][ct] = embedding

            return is_matched_unknown
