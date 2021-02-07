from face_recognition import face_analysis
import cv2
import mxnet as mx
import config
from src import embedding_utils

class face_app:
    def __init__(self):
        self.CAMERA_IDS = [0]
        self.CAMERA_OBJECTS = [cv2.VideoCapture(camera_id) for camera_id in self.CAMERA_IDS]



    def run(self):
        # Gather all frames
        frames = []
        for camera in self.CAMERA_OBJECTS:
            ret, image = camera.read()
            frames.append(image if ret else None)

        for frame in frames:
            faces = face_analysis.get(img=frame, det_scale=config.DETECTION_SCALE)
            for face in faces:
                result = embedding_utils.compare_with_enrolled_data(query=face.embedding)

        return frames[0]


