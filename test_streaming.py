import requests
import json

url = "http://localhost:8000/api/completion"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "sendingData": [
        {"role": "user", "content": "What is the meaning of life?"}
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)

if response.status_code == 200:
    try:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                print(chunk.decode('utf-8'), end='', flush=True)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
else:
    print(f"Failed to connect: {response.status_code}, {response.text}")
