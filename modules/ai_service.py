import requests
import os
import json

# In a real implementation, you would use your actual API key
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your_api_key_here")
GEMINI_API_KEY = "dummy_key_for_development"

def get_ai_response(user_message, device_states):
    """
    Get a response from the Gemini API.
    
    Args:
        user_message (str): The user's message
        device_states (dict): Current state of devices
    
    Returns:
        str: The AI's response
    """
    # For development/testing, return a mock response
    if "weather" in user_message.lower():
        return "The weather is currently sunny with a temperature of 25°C."
    elif "temperature" in user_message.lower():
        return "The current room temperature is shown in the sensor readings section."
    elif "turn on" in user_message.lower():
        device = "light" if "light" in user_message.lower() else "fan"
        return f"I've turned on the {device} for you."
    elif "turn off" in user_message.lower():
        device = "light" if "light" in user_message.lower() else "fan"
        return f"I've turned off the {device} for you."
    elif "hello" in user_message.lower() or "hi" in user_message.lower():
        return "Hello! I'm your smart home assistant. How can I help you today?"
    
    # Real implementation with Gemini API:
    # try:
    #     url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    #     
    #     headers = {
    #         "Content-Type": "application/json",
    #         "x-goog-api-key": GEMINI_API_KEY
    #     }
    #     
    #     data = {
    #         "contents": [{
    #             "parts": [{
    #                 "text": f"""You are a smart home assistant. 
    #                 Current device states: Light is {'ON' if device_states['light'] else 'OFF'}, 
    #                 Fan is {'ON' if device_states['fan'] else 'OFF'}.
    #                 
    #                 User query: {user_message}
    #                 
    #                 Provide a helpful, concise response."""
    #             }]
    #         }]
    #     }
    #     
    #     response = requests.post(url, headers=headers, json=data)
    #     response_json = response.json()
    #     
    #     if response.status_code == 200:
    #         return response_json["candidates"][0]["content"]["parts"][0]["text"]
    #     else:
    #         return f"Sorry, I couldn't process that request. Error: {response.status_code}"
    # except Exception as e:
    #     return f"Sorry, I encountered an error: {str(e)}"
    
    return "I'm your smart home assistant. How can I help you today?"
