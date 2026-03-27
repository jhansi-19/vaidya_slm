import requests
import json
print("Starting request...")
try:
    response = requests.post("http://127.0.0.1:8006/infer", json={"text":"stomach pain", "language":"en"}, timeout=120)
    print("Status:", response.status_code)
    print("Body:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
print("Done")