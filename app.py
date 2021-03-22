import base64
import os
import threading
import traceback
from pathlib import Path
from queue import Queue

import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify, Markup, send_from_directory

import config
from database import db_utils

from src.face_app import Face_app

app = Flask(__name__, template_folder='web', static_folder='web')
queue = None
frame = np.ones((1024, 800), dtype=np.uint8)
if not os.path.exists('./resources'):
    os.makedirs('./resources')


def create_response(status, message):
    data = {}
    data['status'] = status
    data['data'] = message
    return jsonify(data)


@app.route('/', methods=['POST', 'GET'])
def index():
    # data = video_feed_page()
    return render_template('index.html', data=Markup(render_template('src/video_feed.html')))

@app.route('/camera', methods=['POST', 'GET'])
def camera():
    # data = video_feed_page()
    status, data = db_utils.get_active_camera_list()
    return render_template('index.html', data=Markup(render_template('src/camera.html', data=data)))

def gen_frames():
    while True:
        ret, buffer = cv2.imencode('.jpg', frame)
        byte_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_person_page', methods=['POST', 'GET'])
def get_person_page():
    status, data = db_utils.get_enrolled_persons()
    return render_template('index.html', data=Markup(render_template('src/enrol.html', data=data)))


@app.route('/get_person_image', methods=['POST', 'GET'])
def get_person_image():
    image = cv2.imread("/home/jaimin/Downloads/photo.jpg")
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = str(base64.b64encode(buffer))
    print(jpg_as_text)
    return create_response(True, jpg_as_text)


@app.route('/enrol', methods=['POST', 'GET'])
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


@app.route('/enrol_person_entry', methods=['POST', 'GET'])
def enrol_person_entry():
    img_path = request.form.get('img_path')
    name = request.form.get('name')
    if not os.path.exists(img_path) or name is None:
        return create_response(False, "image not exist or name parameter missing")

    image = cv2.imread(img_path)
    data = dict()
    data['add_person'] = {
        'name': name,
        'img': image
    }

    queue.put(data)
    return create_response(True, f'Image added for enrol')

@app.route('/update_enrolled_person', methods=['POST', 'GET'])
def update_enrolled_person():
    entry_id = request.form.get('entry_id')
    if entry_id is None:
        return create_response(False, "entry id parameter missing")

    data = dict()
    data['update_person'] = {
        'entry_id': entry_id,
    }

    queue.put(data)
    return create_response(True, f'Updating person for id {entry_id}')


@app.route('/remove_enrol', methods=['POST', 'GET'])
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


@app.route('/get_entries', methods=['POST', 'GET'])
def get_entries():
    status, data = db_utils.search_entry(**request.form)
    if not status:
        return create_response(False, "Error in fetching entries: " + str(data))

    process_data_abspath = Path(config.PROCESSED_DATA_PATH)
    for i in range(len(data)):
        entry_id = data[i][0]
        data[i].append(os.path.join(str(process_data_abspath), str(entry_id) + '.png'))

    return render_template('index.html', data=Markup(render_template('src/entries.html', data=data)))


@app.route('/get_active_camera', methods=['POST', 'GET'])
def get_active_camera():
    status, camera_paths = db_utils.get_active_camera_list()

    return create_response(True, camera_paths)


@app.route('/add_camera', methods=['POST', 'GET'])
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


@app.route('/remove_camera', methods=['POST', 'GET'])
def remove_camera():
    camera_id = request.form.get('id')
    if camera_id is None:
        return create_response(False, "camera url is missing")

    status, rows_affected = db_utils.remove_camera(id=camera_id)
    data = dict()
    data['update_camera_objects'] = dict()
    queue.put(data)
    return create_response(True, f'{rows_affected} cameras deleted')


@app.route('/resources/<path:filename>')
def send_from_local_dir(filename):
    return send_from_directory('resources', filename, as_attachment=True)


def start_server():
    db_utils.init_database()
    app.run(host='0.0.0.0', port=8090)


if __name__ == "__main__":
    queue = Queue()
    fp = Face_app(queue=queue)

    print("Face app initialized")
    server_process = threading.Thread(target=start_server, daemon=True)
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

    print("Server successfully stopped")
