### Smart Home Voice Assistant

A comprehensive voice-controlled smart home system that allows you to manage and monitor your home devices through voice commands or a web interface. This project combines a Flask backend with a responsive frontend to create an intuitive smart home control center.





## Features

- **Voice Control**: Control your home devices using natural language commands
- **Real-time Monitoring**: View temperature and humidity readings in real-time
- **Device Management**: Control lights, fans, and gates with simple toggles
- **Responsive Design**: Works on desktop and mobile devices
- **Fault Tolerance**: Robust error handling and automatic recovery
- **Hardware Simulation**: Development mode with simulated hardware for testing


## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Hardware**:

- Raspberry Pi
- DHT22 temperature and humidity sensor
- Relay modules for lights and fans
- Servo motor for gate control





## System Architecture

The system consists of two main components:

1. **Flask Backend (`project.py`)**: Handles device control, sensor readings, and processes voice commands
2. **Web Frontend (`index.html`)**: Provides the user interface for monitoring and control


The backend communicates with hardware components through GPIO pins and provides RESTful API endpoints for the frontend to consume.

## Installation

### Prerequisites

- Python 3.7+
- Raspberry Pi (optional - the system can run in development mode without hardware)
- Git


### Step 1: Clone the Repository

```shellscript
git clone https://github.com/yourusername/smart-home-voice-assistant.git
cd smart-home-voice-assistant
```

### Step 2: Create and Activate Virtual Environment

```shellscript
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```shellscript
pip install flask
pip install RPi.GPIO adafruit-circuitpython-dht
```

### Step 4: Run the Application

```shellscript
python project.py
```

The application will start on `http://0.0.0.0:5000`. You can access it from any device on your local network by navigating to `http://[raspberry-pi-ip]:5000`.

## Usage

### Web Interface

The web interface is divided into two main sections:

1. **Voice Assistant Panel**: Allows you to interact with the system using text or voice commands
2. **Control Panel**: Displays sensor readings and provides manual controls for all devices


### Voice Commands

You can control your devices using natural language commands such as:

- "Turn on the light"
- "Turn off the fan"
- "Open the gate"
- "What's the temperature?"
- "What's the humidity level?"


### Manual Controls

Each device has a toggle switch that allows you to control it directly from the interface.

## Adding New Devices

To add a new device to the system:

### 1. Update the Backend (app.py)

Add the new device to the `DEVICE_PINS` dictionary:

```python
DEVICE_PINS = {
    'dht22_1': 4,
    'light_1': 17,
    'fan_1': 27,
    'gate_1': 18,
    'new_device_1': 22  # Add your new device here
}
```

### 2. Update the Frontend (index.html)

Add a new toggle control in the "Device Controls" section:

```html
<div class="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
    <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <!-- Icon for your device -->
        </svg>
        <span class="font-medium">New Device <span id="new-device-status" class="status-dot red-dot"></span></span>
    </div>
    <label class="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" id="new-device-toggle" class="sr-only peer" data-device="new_device_1">
        <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
    </label>
</div>
```

### 3. Add Event Listener in JavaScript

```javascript
const newDeviceToggle = document.getElementById('new-device-toggle');
newDeviceToggle.addEventListener('change', function() {
    if (serverOnline) {
        toggleDevice('new_device_1', this.checked);
    } else {
        this.checked = !this.checked;
        showServerOfflineMessage();
    }
});
```

### 4. Update Voice Command Processing

Add the new device pattern to the `device_patterns` dictionary in the `process_command` function:

```python
device_patterns = {
    'light': r'light(?:s)?(?:\s+(\d+))?',
    'fan': r'fan(?:s)?(?:\s+(\d+))?',
    'gate': r'gate(?:s)?(?:\s+(\d+))?',
    'temperature': r'temperature|temp',
    'humidity': r'humidity|humid',
    'new_device': r'new_device(?:s)?(?:\s+(\d+))?'  # Add pattern for your new device
}
```

## Troubleshooting

### Server Crashes After 30-40 Seconds

If the server crashes after running for a short period:

1. Check for hardware connection issues
2. Ensure you have the latest version of all dependencies
3. Look for error messages in the console output
4. Try running in development mode (without hardware) to isolate the issue


### Voice Recognition Not Working

1. Ensure your browser supports the Web Speech API
2. Check that your microphone is properly connected and has permission
3. Try using the text input as an alternative


### Device Not Responding

1. Verify the GPIO pin connections
2. Check the server logs for hardware-related errors
3. Ensure the device is properly powered
4. Try toggling the device manually through the web interface


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Tailwind CSS](https://tailwindcss.com/) for the UI styling
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) for voice recognition
