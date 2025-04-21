import RPi.GPIO as GPIO
import time
from flask import Flask, jsonify, request
from adafruit_dht import DHT11
import board

app = Flask(__name__)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
DEVICE_PINS = {
    'light1_roomA': 17,
    'fan1_roomA': 27,
    'gate': 18
}
for pin in DEVICE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
servo = GPIO.PWM(DEVICE_PINS['gate'], 50)  # 50 Hz PWM for servo
servo.start(0)
dht1_device = DHT11(board.D4)  # DHT11 on GPIO 4 for sensor ID 1

# Initial states and sensor data
device_states = {device: False for device in DEVICE_PINS.keys()}
sensor_data = {'temperature1': None, 'humidity1': None}

# Log file
LOG_FILE = "sensor_data.log"

def log_data(temp, humi):
    with open(LOG_FILE, 'a') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp}, {temp}°C, {humi}%\n")

def get_sensor_data(sensor_id='1'):
    try:
        temp = dht1_device.temperature
        humi = dht1_device.humidity
        if temp is None or humi is None:
            raise ValueError("Failed to read from DHT1")
        sensor_data[f'temperature{sensor_id}'] = temp
        sensor_data[f'humidity{sensor_id}'] = humi
        log_data(temp, humi)
        return temp, humi
    except Exception as e:
        return None, None

def toggle_device(device, state):
    try:
        if device in DEVICE_PINS:
            if device == 'gate':
                angle = 90 if state else 0
                servo.ChangeDutyCycle(2 + (angle / 18))
                time.sleep(0.5)
                servo.ChangeDutyCycle(0)
            else:
                GPIO.output(DEVICE_PINS[device], GPIO.HIGH if state else GPIO.LOW)
            device_states[device] = state
            return True
        return False
    except Exception as e:
        print(f"Error controlling {device}: {e}")
        return False

def process_command(command_text):
    command_text = command_text.lower().strip()
    words = command_text.split()
    response = "I’m enchanted by your words, but I need a clearer spell!"

    # Control commands
    control_triggers = ['turn', 'switch', 'activate', 'deactivate', 'open', 'close', 'start', 'stop']
    state_indicators = {'on': True, 'open': True, 'start': True, 'activate': True,
                       'off': False, 'close': False, 'stop': False, 'deactivate': False}
    if any(trigger in command_text for trigger in control_triggers) or any(ind in command_text for ind in state_indicators):
        devices = {k: k.replace('_roomA', '') for k in DEVICE_PINS.keys() if 'roomA' in k}
        devices.update({'gate': 'gate'})
        for full_device, short_name in devices.items():
            if short_name in command_text or (short_name.split('_')[0] + ' one' in command_text):
                current_state = device_states.get(full_device, False)
                new_state = None
                for ind, state in state_indicators.items():
                    if ind in command_text:
                        new_state = state
                        break
                if new_state is None and any(trigger in command_text for trigger in ['turn', 'switch', 'activate', 'start']):
                    new_state = not current_state  # Toggle if no explicit state
                elif new_state is None:
                    new_state = True  # Default to on if only trigger
                if current_state != new_state:
                    if toggle_device(full_device, new_state):
                        action = 'on' if new_state else 'off' if full_device != 'gate' else 'closed'
                        response = f"By the glow of my magic, {short_name} in room A is now {action}!"
                    else:
                        response = f"Oh no! My spell faltered on {short_name}—check my runes!"
                else:
                    action = 'on' if current_state else 'off' if full_device != 'gate' else 'closed'
                    response = f"{short_name} in room A is already {action}, my friend!"
                break

    # Status commands
    status_triggers = ['status', 'check', 'what’s', 'tell me', 'show']
    if any(trigger in command_text for trigger in status_triggers):
        if any(sensor in command_text for sensor in ['temperature', 'temp']):
            sensor_id = None
            for i, word in enumerate(words):
                if word in ['temperature', 'temp'] and i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word == 'one' or next_word == '1':
                        sensor_id = '1'
                        break
            sensor_id = sensor_id or '1'  # Default to sensor 1 if not specified
            temp = sensor_data.get(f'temperature{sensor_id}')
            response = f"The temperature from sensor {sensor_id} is {temp}°C, guarded by my warm embrace!" if temp is not None else "I can’t sense the temperature from sensor {sensor_id}—my magic dims!"
        elif 'humidity' in command_text:
            sensor_id = None
            for i, word in enumerate(words):
                if word == 'humidity' and i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word == 'one' or next_word == '1':
                        sensor_id = '1'
                        break
            sensor_id = sensor_id or '1'  # Default to sensor 1 if not specified
            humi = sensor_data.get(f'humidity{sensor_id}')
            response = f"The humidity from sensor {sensor_id} is {humi}%, a misty veil in the air!" if humi is not None else "I can’t feel the humidity from sensor {sensor_id}—my powers fade!"

    return response

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    temp, humi = get_sensor_data()
    if temp is None or humi is None:
        return jsonify({"error": "Sensor reading failed"}), 500
    return jsonify({"temperature1": temp, "humidity1": humi})

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    device = data.get('device')
    state = data.get('state')
    if toggle_device(device, state):
        return jsonify({"status": "success"})
    return jsonify({"error": "Control failed"}), 500

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command_text = data.get('command', '').strip()
    if not command_text:
        return jsonify({"response": "Speak louder, I didn’t catch your wish!"})
    response = process_command(command_text)
    return jsonify({"response": response})

if __name__ == '__main__':
    try:
        get_sensor_data()  # Initial read
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        for pin in DEVICE_PINS.values():
            GPIO.output(pin, GPIO.LOW)
        servo.ChangeDutyCycle(0)
        GPIO.cleanup()
        servo.stop()
