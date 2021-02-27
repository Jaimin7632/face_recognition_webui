"""
MODEL'S PATH
"""
FACE_RECOGNITION_MODEL_PATH = "resources/models/arcface_r100_v1/model-0000.params"
FACE_DETECTION_MODEL_PATH = "resources/models/retinaface_r50_v1/R50-0000.params"

BATCH_SIZE = 4
DETECTION_SCALE = 0.2
UNKNOWN_THRES = 0.87

ENROLLED_DATA_PATH = 'resources/enrolled_data'

USE_GPU = True
VISUALIZE = True

USE_MYSQL_DATABASE = False # if false then sqllite database use
mysql_host = 'host.example.com'
mysql_user = 'domain\\username'
mysql_password = 'password'