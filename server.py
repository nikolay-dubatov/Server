from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
from time import time

app = Flask(__name__) # Создание веб-приложения
CORS(app) # Настройка CORS

# Источник видео (настройте под свой случай)
VIDEO_SOURCE = 1  # 0 — встроенная камера; "rtsp://..." — IP‑камера; "video.mp4" — файл
cap = cv2.VideoCapture(VIDEO_SOURCE)

# ПРеобразования видео с камеры в MJPEG-поток
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
@app.route("/stream")
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
        "capabilities": [
            "forward", "backward", "left", "right", 
            "headlights_on", "headlights_off", 
            "hazard_light_on", "hazard_light_off"
        ]
    })

# Эндпоинт телеметрии (данные с датчиков)
@app.route("/telemetry")
def get_telemetry():
    """
    Эндпоинт для получения данных с датчиков робота.
    Вызывается клиентом каждые 2 секунды для обновления статуса.

    В реальной реализации здесь будет чтение с физических датчиков.
    Сейчас — тестовые данные.
    """
    data = {
        "battery": 85,  # Уровень заряда батареи в процентах
        "temperature": 32,  # Температура процессора/двигателей в °C
        "speed": 0,  # Текущая скорость движения в км/ч
        "heading": 90,  # Направление движения в градусах (0° = север)
        "obstacle_distance": 150  # Расстояние до препятствия в см (с ультразвукового датчика)
    }
    return jsonify({
        "status": "ok", 
        "data": data, # Основные данные
        "timestamp": time() # Временная метка для синхронизации
    })

# --- Эндпоинт предустановленных режимов ---
@app.route("/mode/<mode_name>")
def set_mode(mode_name):
    """
    Установка предустановленного режима работы.
    Принимает имя режима через URL (например, /mode/parking).

    Аргумент:
        mode_name (str): имя режима из словаря modes
    """
    # Словарь режимов: каждому режиму — список команд для выполнения
    modes = {
        'parking': ['parking_lights_on', 'stop'],  # Парковка: габариты + остановка
        'offroad': ['low_beam_on', 'parking_lights_on'],  # Бездорожье: ближний свет + габариты
        'emergency': ['hazard_lights_on', 'stop']  # Аварийный: аварийка + остановка
    }
    if mode_name in modes:
        # Выполняем все команды режима последовательно
        for command in modes[mode_name]:
            send_command(command)
        return jsonify({
            "status": "ok", 
            "mode": mode_name
        })
    else: 
        return jsonify({
            "status": "error", 
            "message": "Неизвестный режим"
        }), 400

@app.route("/<command>")
def send_command(command):
    """Универсальный обработчик команд управления."""
    print(f"Получена команда: {command}")
    # Словарь команд
    command_messages = {
        "forward": "Движение вперёд",
        "backward": "Движение назад",
        "left": "Поворот влево",
        "right": "Поворот вправо",
        "stop": "Остановка",
        "headlights_on": "Фары включены",
        "headlights_off": "Фары выключены",
        "hazard_lights_on": "Аварийная сигнализация включена",
        "hazard_lights_off": "Аварийная сигнализация выключена", 
        "parking_lights_on": "Габаритные огни включены", 
        "parking_lights_off": "Габаритные огни выключены"
    }
    # Вывод выполненной команды
    if command in command_messages:
        action = command_messages[command]
    else:
        return jsonify({
            "status": "error", 
            "message": f"Неизвестная команда: {command}"
        }), 400
    return jsonify({
        "status": "ok", 
        "command": command, 
        "message": action
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)