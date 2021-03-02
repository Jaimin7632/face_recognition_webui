import base64
import traceback

from src.face_app import Face_app
import cv2
import os
import numpy as np
from queue import Queue
from flask import Flask, render_template, Response, request, jsonify,Markup

from database import db_utils

app = Flask(__name__, template_folder='web', static_folder='web')
queue = None
frame = np.ones((1024,800), dtype=np.uint8)
if not os.path.exists('./resources'):
    os.makedirs('./resources')


def create_response(status, message):
    data = {}
    data['status'] = status
    data['data'] = message
    return jsonify(data)


@app.route('/', methods=['POST','GET'])
def index():
    # data = video_feed_page()
    status, data = db_utils.get_active_camera_list()
    return render_template('index.html',data=Markup(render_template('src/video_feed.html', data=data)))


def gen_frames():
    while True:
        ret, buffer = cv2.imencode('.jpg', frame)
        byte_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_person_page', methods=['POST','GET'])
def get_person_page():
    status, data = db_utils.get_enrolled_persons()
    return render_template('index.html',data=Markup(render_template('src/person.html', data=data)))


@app.route('/get_person_image', methods=['POST','GET'])
def get_person_image():
    image = cv2.imread("/home/jaimin/Downloads/photo.jpg")
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = str(base64.b64encode(buffer))
    print(jpg_as_text)
    return create_response(True, jpg_as_text)


@app.route('/enrol', methods=['POST','GET'])
def enrol_person():
    image = request.files.get('image')
    name = request.form.get('name')
    if image is None or name is None:
        return create_response(False, "image or name parameter missing")

    npimg = np.frombuffer(image.read(), dtype=np.uint8)
    # convert numpy array to image
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    data = dict()
    data['add_person'] = {
        'name': name,
        'img': image
    }

    queue.put(data)
    return create_response(True, f'Image added for enrol')


@app.route('/remove_enrol', methods=['POST','GET'])
def remove_enrol():
    id = request.form.get('id')

    if id is None:
        return create_response(False, "id parameter missing")
    data = dict()
    data['remove_person'] = {
        'id': id
    }
    queue.put(data)
    return create_response(True, f'Person Removed')


@app.route('/get_entries', methods=['POST','GET'])
def get_entries():
    status, data = db_utils.search_entry(**request.form)
    if not status:
        return create_response(False, "Error in featching entries: " + str(data))

    return render_template('index.html',data=Markup(render_template('src/entry.html', data=data)))


@app.route('/get_active_camera', methods=['POST','GET'])
def get_active_camera():
    status, camera_paths = db_utils.get_active_camera_list()

    return create_response(True, camera_paths)


@app.route('/add_camera', methods=['POST','GET'])
def add_camera():
    camera_str = request.form.get('camera_url')
    if camera_str is None:
        return create_response(False, "camera url is missing")

    data = dict()
    data['add_camera'] = {
        'camera_path': camera_str
    }
    queue.put(data)
    return create_response(True, f'{camera_str} is added')


@app.route('/remove_camera', methods=['POST','GET'])
def remove_camera():
    camera_id = request.form.get('id')
    if camera_id is None:
        return create_response(False, "camera url is missing")

    status, rows_affected = db_utils.remove_camera(id=camera_id)
    data = dict()
    data['update_camera_objects'] = dict()
    queue.put(data)
    return create_response(True, f'{rows_affected} cameras deleted')


def start_server():
    db_utils.init_database()
    app.run(host='0.0.0.0', port=8080)

import threading
if __name__ == "__main__":
    queue = Queue()
    fp = Face_app(queue=queue)

    print("Face app initialized")
    server_process = threading.Thread(target=start_server)
    server_process.start()
    print("Server started")

    while True:
        image = None
        try:
            image = fp.run()
            if image is not None:
                frame = cv2.resize(image, (1024, 800))
        except KeyboardInterrupt:
            print('keyboard intrupt')
            traceback.print_exc()
            break
        except Exception as e:
            traceback.print_exc()
            print(e)
            break

    server_process.terminate()
    print("Server successfully stopped")
