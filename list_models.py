import requests
import json

API_KEY = "AIzaSyDVvtjXvKl6JstvS8J83zLj5ri0HVL5vMA"
URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

def list_models():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Found {len(models)} models:")
            for m in models:
                if 'generateContent' in m['supportedGenerationMethods'] and 'gemini' in m['name']:
                    print(f"- {m['name']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_models()
