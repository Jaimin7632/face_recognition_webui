from database import db_utils
from src.face_app import Face_app
import cv2
from flask import Flask, render_template, Response, request, jsonify
from multiprocessing import Process
import traceback
from multiprocessing import Queue

app = Flask(__name__,template_folder='frontend_templates')
queue = None
frame = None

def create_response(status, message):
    data= {}
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


@app.route('/enrol', methods=['POST'])
def enrol_person():
    image = request.files['image']
    name = request.form['name']

    if image is None or name is None:
        return create_response(False, "image or name parameter missing")
    data= dict()
    data['add_person'] = {
        'name': name,
        'img': image
    }
    queue.put(data)
    return create_response(True, f'{name} is added for enrol')

@app.route('/remove_enrol', methods=['POST'])
def remove_enrol_person():
    name = request.value['id']

    if id is None:
        return create_response(False, "id parameter missing")
    data= dict()
    data['remove_person'] = {
        'id': id
    }
    queue.put(data)
    return create_response(True, f'{name} is added for enrol')

def start_server():
    db_utils.init_database()
    app.run(host='0.0.0.0', debug=True)

if __name__=="__main__":
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
