from flask import Flask, jsonify, request, render_template
import json
import os
import time
import re
from difflib import get_close_matches
import threading

# Mock GPIO for development - replace with actual GPIO on Raspberry Pi
try:
    import RPi.GPIO as GPIO
    from adafruit_dht import DHT22
    import board
    HARDWARE_AVAILABLE = True
except ImportError:
    print("Running in development mode - hardware simulation active")
    HARDWARE_AVAILABLE = False

app = Flask(__name__, static_folder='.', template_folder='.')

# Device configuration
DEVICE_PINS = {
    'dht22_1': 4,  # DHT22 sensor on pin 4
    'light_1': 17,  # Light on pin 17
    'fan_1': 27,    # Fan on pin 27
    'gate_1': 18    # Gate (servo) on pin 18
}

# Data storage
DATA_FILE = "device_states.json"

# Initialize device states
def load_device_states():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'devices': {device: False for device in DEVICE_PINS.keys()},
        'sensors': {'temperature': 22.5, 'humidity': 45.0},
        'sensor_status': True
    }

# Save device states
def save_device_states(states):
    with open(DATA_FILE, 'w') as f:
        json.dump(states, f)

# Global state
state = load_device_states()

# Lock for DHT22 access
dht_lock = threading.Lock()

# Initialize GPIO and DHT22
if HARDWARE_AVAILABLE:
    try:
        GPIO.setmode(GPIO.BCM)
        for device, pin in DEVICE_PINS.items():
            if device != 'dht22_1':
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH if state['devices'].get(device, False) else GPIO.LOW)

        # Initialize servo for gate
        servo = GPIO.PWM(DEVICE_PINS['gate_1'], 50)
        servo.start(0)

        # Initialize DHT22
        dht_device = DHT22(board.D4)
    except Exception as e:
        print(f"Error initializing hardware: {e}")
        HARDWARE_AVAILABLE = False

# Fetch DHT22 data with detailed logging
def fetch_dht22_data():
    if HARDWARE_AVAILABLE:
        with dht_lock:  # Ensure exclusive access to DHT22
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                print(f"Raw DHT22 read: Temp={temperature}, Humi={humidity}")
                if temperature is not None and humidity is not None:
                    print(f"DHT22 read successful: Temp={temperature:.1f}°C, Humi={humidity:.1f}%")
                    return temperature, humidity
                else:
                    print("Failed to read DHT22, retrying...")
                    return None, None
            except Exception as e:
                print(f"DHT22 error: {e}")
                return None, None
    else:
        return None, None

# Read sensor data with retry logic
def read_sensor_data():
    if HARDWARE_AVAILABLE:
        for attempt in range(3):
            temp, humi = fetch_dht22_data()
            if temp is not None and humi is not None:
                state['sensors']['temperature'] = temp
                state['sensors']['humidity'] = humi
                state['sensor_status'] = True
                return temp, humi
            time.sleep(2)
        state['sensor_status'] = False
        print("DHT22 read failed after all retries")
        return None, None
    else:
        state['sensors']['temperature'] = round(state['sensors']['temperature'] + (0.1 * (time.time() % 10 - 5)), 1)
        state['sensors']['humidity'] = round(state['sensors']['humidity'] + (0.1 * (time.time() % 10 - 5)), 1)
        return state['sensors']['temperature'], state['sensors']['humidity']

# Standalone test for DHT22 (limited iterations)
def test_dht22_standalone():
    print("Starting standalone DHT22 test (5 iterations)...")
    for i in range(5):
        temp, humi = fetch_dht22_data()
        if temp is not None and humi is not None:
            print(f"Standalone test (iteration {i+1}): Temperature: {temp:.1f}°C  Humidity: {humi:.1f}%")
        else:
            print(f"Standalone test (iteration {i+1}): Error: Could not fetch data from DHT22 sensor.")
        time.sleep(2)
    print("Standalone test complete.")

# Control a device
def control_device(device, status):
    if device not in DEVICE_PINS:
        return False

    state['devices'][device] = status
    save_device_states(state)

    if HARDWARE_AVAILABLE:
        try:
            if device == 'gate_1':
                angle = 90 if status else 0
                servo.ChangeDutyCycle(2 + (angle / 18))
                time.sleep(0.5)
                servo.ChangeDutyCycle(0)
            else:
                GPIO.output(DEVICE_PINS[device], GPIO.HIGH if status else GPIO.LOW)
            return True
        except Exception as e:
            print(f"Error controlling device {device}: {e}")
            return False
    return True

# Process voice commands
def process_command(command):
    command = command.lower().strip()

    device_patterns = {
        'light': r'light(?:s)?(?:\s+(\d+))?',
        'fan': r'fan(?:s)?(?:\s+(\d+))?',
        'gate': r'gate(?:s)?(?:\s+(\d+))?',
        'temperature': r'temperature|temp',
        'humidity': r'humidity|humid'
    }

    action_patterns = {
        'on': r'\b(turn|switch|put)\s+on\b|\bon\b',
        'off': r'\b(turn|switch|put)\s+off\b|\boff\b',
        'open': r'\bopen\b',
        'close': r'\bclose\b',
        'status': r'\b(status|how|what|reading|level)\b'
    }

    detected_device = None
    device_number = "1"

    for device, pattern in device_patterns.items():
        match = re.search(pattern, command)
        if match:
            detected_device = device
            if match.groups() and match.group(1):
                device_number = match.group(1)
            break

    detected_action = None

    for action, pattern in action_patterns.items():
        if re.search(pattern, command):
            detected_action = action
            break

    if detected_device and detected_action:
        if detected_device in ['temperature', 'humidity'] and detected_action == 'status':
            read_sensor_data()
            if detected_device == 'temperature':
                return f"The current temperature is {state['sensors']['temperature']}°C"
            else:
                return f"The current humidity is {state['sensors']['humidity']}%"

        device_id = f"{detected_device}_{device_number}"

        if device_id in state['devices']:
            if detected_action in ['on', 'open']:
                control_device(device_id, True)
                return f"The {detected_device} {device_number} has been turned on."
            elif detected_action in ['off', 'close']:
                control_device(device_id, False)
                return f"The {detected_device} {device_number} has been turned off."
            elif detected_action == 'status':
                status = "on" if state['devices'].get(device_id, False) else "off"
                return f"The {detected_device} {device_number} is currently {status}."

    return "I'm sorry, I didn't understand that command. Please try again."

# Routes
@app.route('/')
def index():
    print("Serving dashboard at /")
    return render_template('project.html')

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    print("Fetching sensor data for /api/sensors")
    temperature, humidity = read_sensor_data()
    response = {
        'temperature1': temperature,
        'humidity1': humidity,
        'status': {'dht1': state['sensor_status']}
    }
    print(f"Sensor endpoint response: {response}")
    return jsonify(response)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    print("Fetching device states for /api/devices")
    return jsonify({'devices': state['devices']})

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    device = data.get('device')
    status = data.get('state')
    print(f"Control request: device={device}, state={status}")
    success = control_device(device, status)
    return jsonify({
        'status': 'success' if success else 'error',
        'device_state': state['devices'].get(device, False)
    })

@app.route('/api/command', methods=['POST'])
def command():
    data = request.json
    command_text = data.get('command', '')
    print(f"Command received: {command_text}")
    if not command_text:
        return jsonify({'response': 'I didn\'t hear anything. Please try again.'})
    response = process_command(command_text)
    return jsonify({'response': response})

@app.route('/api/health', methods=['GET'])
def health_check():
    print("Health check at /api/health")
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Run standalone test first to verify DHT22
    if HARDWARE_AVAILABLE:
        test_dht22_standalone()
        print("Starting Flask server...")

    try:
        print("Flask server starting on 0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        if HARDWARE_AVAILABLE:
            try:
                GPIO.cleanup()
                dht_device.exit()
                print("Cleaned up GPIO and DHT22 resources")
            except Exception as e:
                print(f"Error during cleanup: {e}")
