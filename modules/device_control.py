# In a real implementation, you would use:
# import RPi.GPIO as GPIO

# GPIO pin mapping
PIN_MAPPING = {
    "light": 17,  # GPIO pin for light
    "fan": 18     # GPIO pin for fan
}

def setup_gpio():
    """
    Set up GPIO pins for device control.
    Uncomment for real Raspberry Pi implementation.
    """
    # GPIO.setmode(GPIO.BCM)
    # for pin in PIN_MAPPING.values():
    #     GPIO.setup(pin, GPIO.OUT)
    #     GPIO.output(pin, GPIO.LOW)
    pass

def toggle_device(device, state):
    """
    Toggle a device on or off.
    
    Args:
        device (str): The device to control ('light' or 'fan')
        state (bool): True for on, False for off
    """
    if device not in PIN_MAPPING:
        print(f"Unknown device: {device}")
        return False
    
    # For development/testing, just print the action
    print(f"Setting {device} to {'ON' if state else 'OFF'}")
    
    # Real implementation with GPIO:
    # pin = PIN_MAPPING[device]
    # GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
    
    return True

# Initialize GPIO on module import
setup_gpio()
