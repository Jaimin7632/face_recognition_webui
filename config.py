"""
MODEL'S PATH
"""
FACE_RECOGNITION_MODEL_PATH = "resources/models/arcface_r100_v1/model-0000.params"
FACE_DETECTION_MODEL_PATH = "resources/models/retinaface_r50_v1/R50-0000.params"
FACE_LANDMARKS_MODEL_PATH = "resources/models/2d106det/2d106det"

BATCH_SIZE = 4
DETECTION_SCALE = 0.3
UNKNOWN_THRES = 1.05

ENROLLED_DATA_PATH = 'resources/enrolled_data'
PROCESSED_DATA_PATH = 'resources/crops_data'

USE_GPU = True
VISUALIZE = True

USE_MYSQL_DATABASE = False # if false then sqllite database use
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'password'