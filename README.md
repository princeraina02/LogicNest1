### Voice-Controlled Smart Home Assistant for Raspberry Pi 4

I'll create a complete solution for your voice-controlled smart home assistant using a Raspberry Pi 4. The system will use a web-based dashboard with a microphone button to trigger voice input, process commands via Gemini API, and control your smart home devices.

## Project Structure

```typescriptreact project="smart_home_assistant"
...
```

## How It Works

This smart home assistant combines a Flask backend with a web-based frontend to create a voice-controlled system:

1. **Voice Input**: Click the microphone button on the dashboard to activate the Web Speech API, which captures your voice and converts it to text.
2. **AI Processing**: The transcribed text is sent to the Flask backend, which processes it using a simulated Gemini API response (in production, you'd use the actual Gemini API).
3. **Device Control**: The system can control GPIO pins on your Raspberry Pi to toggle devices like lights and fans.
4. **Sensor Monitoring**: The dashboard displays real-time temperature and humidity readings from a DHT22 sensor (simulated in the code, but ready for real implementation).
5. **Voice Response**: The assistant responds both visually on the dashboard and audibly using the browser's speech synthesis capabilities.


## Setup Instructions

1. **Install Dependencies**:

```shellscript
pip install flask adafruit-dht RPi.GPIO requests
```


2. **Project Structure**:
Create the following directory structure:

```plaintext
smart_home_assistant/
├── app.py
├── modules/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── device_control.py
│   └── sensors.py
└── templates/
    └── index.html
```


3. **Run the Application**:

```shellscript
python app.py
```


4. **Access the Dashboard**:
Open a browser on your network and navigate to `http://[raspberry-pi-ip]:5000`


## Production Notes

1. For production use, uncomment the actual hardware interaction code in:

1. `sensors.py` to use the real DHT22 sensor
2. `device_control.py` to control actual GPIO pins
3. `ai_service.py` to use the real Gemini API



2. Add your Gemini API key as an environment variable:

```shellscript
export GEMINI_API_KEY="your_api_key_here"
```


3. Adjust the GPIO pin numbers in `device_control.py` to match your actual hardware setup.


This implementation provides a clean, functional smart home assistant that runs entirely on your Raspberry Pi with minimal dependencies.
