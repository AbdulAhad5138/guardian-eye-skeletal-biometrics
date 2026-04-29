import requests
import json

api_url = "http://localhost:8000/api/access_event"
payload = {"timestamp": 1234, "credential_id": "USER_A", "door_id": "FRONT_DOOR"}
r = requests.post(api_url, json=payload)
print(json.dumps(r.json(), indent=4))
