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

"""
Database 
- Default SqlLite db is used
- For use MsSQL 
    - CREATE DATABASE {DATABASE_NAME} 
    - Change flag in config
"""
USE_MSSQL_DATABASE = False
database_name = 'face_recognition_db'
mssql_host = 'localhost'
mssql_user = 'root'
mssql_password = 'password'
