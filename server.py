from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
from datetime import datetime

app = Flask(__name__)
CORS(app)

VIDEO_SOURCE = 1
cap = cv2.VideoCapture(VIDEO_SOURCE)

# Преобразования видео с камеры в MJPEG-поток
def generate_frames():
    """Генератор кадров из источника видео."""
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Кодируем кадр в JPEG
            frame = cv2.resize(frame, (640, 480))
            ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            # Формируем часть MJPEG‑потока
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

# Эндпоинт для видеопотока
@app.route("/camera/stream")
def video_feed():
    """Эндпоинт для видеопотока."""
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/discover")
def discover():
    """Эндпоинт для обнаружения сервера."""
    return jsonify({
        "status": "ok", 
        "device_type": "test_server",
        "name": "Car Test Server", 
        "version": "1.0", 
    })

# Эндпоинт телеметрии (данные с датчиков)
@app.route("/telemetry")
def get_telemetry():
    data = {
        "battery": 85,  # Уровень заряда батареи в процентах
        "obstacle_distance": 150  # Расстояние до препятствия в см (с ультразвукового датчика)
    }
    now = datetime.now()
    return jsonify({
        "status": "ok", 
        "data": data, # Основные данные
        "timestamp": now.strftime("%H:%M:%S") # Временная метка для синхронизации
    })
@app.route('/car/commands')
def move_car():
    commands = [
        "stop", 
        "left", 
        "right", 
        "forward", 
        "backward"
    ]
    command = request.args.get('command')
    if command in commands:
        return jsonify({
            "status": "ok", 
            "message": f"Команда {command} выполнена", 
        })
    else:
        return jsonify({
            "status": "error", 
            "message": f"Неизвестная команда: {command}"
        }), 400
@app.route("/car/speed")
def select_speed():
    levels = [
        "low", 
        "medium", 
        "high"
    ]
    speed = request.args.get('level')
    if speed in levels: 
        return jsonify({
            "status": "ok", 
            "message": f"Установлена скорость: {speed}"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": f"Неизвестная команда: {speed}"
        }), 400
@app.route("/camera/control")
def control_camera():
    commands = [
        "cam-stop", 
        "cam-down", 
        "cam-up", 
        "cam-left", 
        "cam-right"
    ]
    command = request.args.get('command')
    if command in commands: 
        return jsonify({
            "status": "ok", 
            "message": f"Команда {command} выполнена"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": f"Неизвестная команда: {command}"
        }), 400
@app.route('/car/lights/<name>')
def turn_lights(name):
    names = [
        "headlights", 
        "hazard_lights", 
        "parking_lights"
    ]
    states = [
        "on", "off"
    ]
    state = request.args.get('state')
    if name in names and state in states:
        return jsonify({
            "status": "ok", 
            "message": f"{name}: {state}"
        })
    else: 
        return jsonify({
            "status":"error", 
            "message": f"Неизвестная команда: {name}&{state=}"
        }), 400
@app.route('/car/horn')
def horn():
    return jsonify({
        "status": "ok", 
        "message": "Гудок"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)