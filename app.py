from flask import Flask, render_template, request, jsonify
import json
import os
from modules.sensors import get_sensor_readings
from modules.device_control import toggle_device
from modules.ai_service import get_ai_response
import threading
import time

app = Flask(__name__)

# Store the current state of devices
device_states = {
    "light": False,
    "fan": False
}

# Background thread for sensor readings
sensor_data = {"temperature": 0, "humidity": 0}

def sensor_thread():
    while True:
        sensor_data.update(get_sensor_readings())
        time.sleep(5)  # Update every 5 seconds

# Start sensor thread
threading.Thread(target=sensor_thread, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get response from AI service
    response = get_ai_response(user_message, device_states)
    
    # Check if the response contains a command to control devices
    if "turn on light" in user_message.lower():
        toggle_device("light", True)
        device_states["light"] = True
    elif "turn off light" in user_message.lower():
        toggle_device("light", False)
        device_states["light"] = False
    elif "turn on fan" in user_message.lower():
        toggle_device("fan", True)
        device_states["fan"] = True
    elif "turn off fan" in user_message.lower():
        toggle_device("fan", False)
        device_states["fan"] = False
    
    return jsonify({"response": response})

@app.route('/api/sensors', methods=['GET'])
def sensors():
    return jsonify(sensor_data)

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    device = data.get('device')
    state = data.get('state')
    
    if device not in ["light", "fan"]:
        return jsonify({"error": "Invalid device"}), 400
    
    # Update device state
    device_states[device] = state
    
    # Control the physical device
    toggle_device(device, state)
    
    return jsonify({"device": device, "state": state})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
