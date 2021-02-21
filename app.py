import base64
import traceback
from multiprocessing import Process
from multiprocessing import Queue

from src.face_app import Face_app
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify

from database import db_utils

app = Flask(__name__, template_folder='web', static_folder='web')
queue = None
frame = np.ones((500, 500), dtype=np.uint8)


def create_response(status, message):
    data = {}
    data['status'] = status
    data['data'] = message
    return jsonify(data)


@app.route('/')
def index():
    return render_template('index.html')


def gen_frames():
    while True:
        ret, buffer = cv2.imencode('.jpg', frame)
        byte_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_person_page')
def get_person_page():
    status, data = db_utils.get_enrolled_persons()
    return render_template('src/person.html', data=data)


@app.route('/get_person_image', methods=['POST'])
def get_person_image():
    image = cv2.imread("/home/jaimin/Downloads/photo.jpg")
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = str(base64.b64encode(buffer))
    print(jpg_as_text)
    return create_response(True, jpg_as_text)


@app.route('/enrol', methods=['POST'])
def enrol_person():
    image = request.files.get('image')
    name = request.form.get('name')
    if image is None or name is None:
        return create_response(False, "image or name parameter missing")

    npimg = np.fromstring(image.read(), np.uint8)
    # convert numpy array to image
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    data = dict()
    data['add_person'] = {
        'name': name,
        'img': image
    }

    queue.put(data)
    return create_response(True, f'{name} is added for enrol')


@app.route('/remove_enrol', methods=['POST'])
def remove_enrol_person():
    id = request.form.get('id')

    if id is None:
        return create_response(False, "id parameter missing")
    data = dict()
    data['remove_person'] = {
        'id': id
    }
    queue.put(data)
    return create_response(True, f'Person Removed')


@app.route('/get_entries', methods=['GET', 'POST'])
def get_entries():
    status, data = db_utils.search_entry(**request.form)
    if not status:
        return create_response(False, "Error in featching entries: " + str(data))

    return render_template('src/entry.html', data=data)


@app.route('/get_active_camera', methods=['POST'])
def get_active_camera():
    status, camera_paths = db_utils.get_active_camera_list()

    return create_response(True, camera_paths)


@app.route('/add_camera', methods=['POST'])
def add_camera():
    camera_str = request.form.get('camera_url')
    if camera_str is None:
        return create_response(False, "camera url is missing")

    status, camera_id = db_utils.add_camera(camera_path=camera_str)

    return create_response(True, f'{camera_str} is added')


@app.route('/remove_camera', methods=['POST'])
def remove_camera():
    camera_str = request.form.get('camera_url')
    if camera_str is None:
        return create_response(False, "camera url is missing")

    status, rows_affected = db_utils.remove_camera(camera_path=camera_str)

    return create_response(True, f'{rows_affected} cameras deleted')


def start_server():
    db_utils.init_database()
    app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    queue = Queue()
    fp = Face_app(queue=queue)

    print("Face app initialized")
    server_process = Process(target=start_server)
    server_process.start()
    print("Server started")

    while True:
        try:
            image = fp.run()
            if image is not None:
                frame = image
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
