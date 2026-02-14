#!/usr/bin/env python3
import requests
import json

url = "http://localhost:5000/api/auth/login"
data = {
    "email": "claudetest@example.com",
    "password": "TestPassword123!"
}

print(f"Testing login with: {data['email']}")
print(f"Password length: {len(data['password'])}")

response = requests.post(url, json=data)
print(f"\nStatus Code: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
