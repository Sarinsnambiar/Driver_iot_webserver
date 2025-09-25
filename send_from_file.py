import json
import requests

# Load data from the file
with open('data/health.json') as f:
    data = json.load(f)

# Send to server
response = requests.post("http://localhost:5000/api/update", json=data)
print("Response:", response.text)
