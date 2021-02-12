from src.face_app import face_app
import cv2
from flask import Flask, render_template, Response
from multiprocessing import Process
import traceback

app = Flask(__name__)
frame = None

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


def start_server():
    app.run(host='0.0.0.0', debug=True)

if __name__=="__main__":
    fp = face_app()
    print("Face app initialized")
    # server_process = Process(target=start_server)
    # server_process.start()
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

    # server_process.terminate()
    print("Server successfully stopped")
