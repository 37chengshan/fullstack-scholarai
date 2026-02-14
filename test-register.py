#!/usr/bin/env python3
import requests
import json

url = "http://localhost:5000/api/auth/register"
data = {
    "name": "Claude Test",
    "email": "claudetest@example.com",
    "password": "TestPassword123!"
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
