import face_recognition
import cv2

CAMERA_IDS = [0]
CAMERA_OBJECTS = [cv2.VideoCapture(camera_id) for camera_id in CAMERA_IDS]
def run():
    # Capture frames
    frames = []
    for camera in CAMERA_OBJECTS:
        ret, image = camera.read()
        frames.append(image if ret else None)



