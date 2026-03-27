import requests
import json

url = "http://127.0.0.1:8005/infer"
data = {
    "text": "How can I reduce hairfall according to Ayurveda?",
    "language": "en"
}

print(f"Testing endpoint: {url}")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error connecting to backend: {e}")
