# Сервер для тестирования машинки
Используется для симуляции машинки для управления 
через [веб-клиент](https://github.com/nikolay-dubatov/Client). 
## Инструкция
1. Запустить сервер в локальной сети. Для этого должен быть 
установлен Python и библиотеки из requirements.txt командой
**в виртуальной среде**
    ``` bash
    pip install -r requirements.txt
    ```
2. Запустить клиент в той же сети или настроить проброс портов. 
3. Подключиться через веб-клиент. 
4. Всё готово! 
## API
- `/camera/stream` MJPEG-поток
- `/camera/control?command=` Поворот камеры
    - command= `cam-stop` / `cam-up` / `cam-down` / `cam-left` / `cam-right`
- `/car/control?command` Управление машинкой
    - command= `stop` / `right` / `left` / `forward` / `backward`
- `/car/speed?level=` Управление скоростью
    - level= `low` / `medium` / `high`
- `/car/lights/<name>?state=` Управление фарами
    - name= `headlights` / `hazard_lights` / `parking_lights`
    - state= `on` / `off`
- `/car/horn` Подача звукового сигнала
- `/telemetry` Телеметрия <br>
\-> 
    ``` json
    {
        "status": "ok", 
        "data": {
            "battery": 85, 
            "obstacle_distance": 150
        }, 
        "timestamp": "12:30:15"
    }
    ```
- `/discover` Эндпоинт для обнаружения <br>
\->
    ``` json
    {
        "status": "ok", 
            "device_type": "test_server",
            "name": "Car Test Server", 
            "version": "1.0"
    }
    ```