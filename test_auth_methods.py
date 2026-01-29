import requests
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS", "").strip()
API_KEY = os.getenv("DEHASHED_API_KEY", "").strip()

print(f"Testing DeHashed API with email:key headers...")
print(f"Email: {EMAIL}")
print(f"API Key: {API_KEY[:4]}...{API_KEY[-4:]}\n")

# Try different authentication methods
methods = [
    {
        'name': 'Basic Auth with Base64',
        'auth': (EMAIL, API_KEY),  # Let requests handle it
        'headers': {'Accept': 'application/json'}
    },
    {
        'name': 'X-API-Email and X-API-Key headers',
        'auth': None,
        'headers': {
            'Accept': 'application/json',
            'X-API-Email': EMAIL,
            'X-API-Key': API_KEY
        }
    },
    {
        'name': 'API-Email and API-Key headers',
        'auth': None,
        'headers': {
            'Accept': 'application/json',
            'API-Email': EMAIL,
            'API-Key': API_KEY
        }
    }
]

url = "https://api.dehashed.com/search"
params = {'query': 'email:test@example.com'}

for method in methods:
    print(f"\n{'='*60}")
    print(f"Testing: {method['name']}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(
            url, 
            headers=method['headers'],
            auth=method['auth'],
            params=params
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")
