import requests

url = "http://127.0.0.1:8005/infer"
data = {
    "text": "stomach pain",
    "language": "en"
}

try:
    response = requests.post(url, json=data)
    print("Status:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
