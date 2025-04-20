import random

# In a real implementation, you would use:
# import Adafruit_DHT

def get_sensor_readings():
    """
    Get temperature and humidity readings from DHT22 sensor.
    
    For development/testing, this returns random values.
    In production, uncomment the Adafruit_DHT code.
    """
    # Simulate sensor readings for development
    temperature = round(random.uniform(20.0, 30.0), 1)
    humidity = round(random.uniform(40.0, 60.0), 1)
    
    # Real implementation with DHT22 sensor:
    # sensor = Adafruit_DHT.DHT22
    # pin = 4  # GPIO pin where DHT22 is connected
    # humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    # if humidity is not None and temperature is not None:
    #     temperature = round(temperature, 1)
    #     humidity = round(humidity, 1)
    # else:
    #     temperature = 0
    #     humidity = 0
    
    return {
        "temperature": temperature,
        "humidity": humidity
    }
