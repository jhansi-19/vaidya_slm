import requests
import json

url = "http://127.0.0.1:8000/infer"
data = {"text": "I have tinnitus and dry skin", "language": "en"}

try:
    response = requests.post(url, json=data)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
