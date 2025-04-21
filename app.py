import RPi.GPIO as GPIO
import time
from flask import Flask, jsonify, request
from adafruit_dht import DHT11
import board

app = Flask(__name__)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
LIGHT_PIN = 17  # GPIO 17 for light1
FAN_PIN = 27    # GPIO 27 for fan1
SERVO_PIN = 18  # GPIO 18 for servo motor (gate)
GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM for servo
servo.start(0)
dht_device = DHT11(board.D4)  # DHT11 on GPIO 4 (adjust pin as per wiring)

# Initial states
GPIO.output(LIGHT_PIN, GPIO.LOW)
GPIO.output(FAN_PIN, GPIO.LOW)

# Log file for local data storage
LOG_FILE = "sensor_data.log"

def log_data(temp, humi):
    with open(LOG_FILE, 'a') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp}, {temp}°C, {humi}%\n")

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    try:
        temp = dht_device.temperature
        humi = dht_device.humidity
        if temp is None or humi is None:
            raise ValueError("Failed to read from DHT11")
        log_data(temp, humi)
        return jsonify({"temperature": temp, "humidity": humi})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    device = data.get('device')
    state = data.get('state')

    try:
        if device == 'light1':
            GPIO.output(LIGHT_PIN, GPIO.HIGH if state else GPIO.LOW)
        elif device == 'fan1':
            GPIO.output(FAN_PIN, GPIO.HIGH if state else GPIO.LOW)
        elif device == 'gate':
            angle = 90 if state else 0
            servo.ChangeDutyCycle(2 + (angle / 18))  # Convert angle to duty cycle
            time.sleep(0.5)  # Allow servo to move
            servo.ChangeDutyCycle(0)
        else:
            return jsonify({"error": "Unknown device"}), 400
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        GPIO.output(LIGHT_PIN, GPIO.LOW)
        GPIO.output(FAN_PIN, GPIO.LOW)
        servo.ChangeDutyCycle(0)
        GPIO.cleanup()
        servo.stop()
