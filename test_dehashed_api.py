import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS", "").strip()
API_KEY = os.getenv("DEHASHED_API_KEY", "").strip()

print(f"Testing DeHashed API...")
print(f"Email: {EMAIL}")
print(f"API Key: {API_KEY[:4]}...{API_KEY[-4:]}\n")

# Test with manual Basic Auth
credentials = f"{EMAIL}:{API_KEY}"
encoded = base64.b64encode(credentials.encode()).decode()

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {encoded}',
    'User-Agent': 'TestScript/1.0'
}

# Try both endpoints
for endpoint in ['/search', '/v2/search']:
    url = f"https://api.dehashed.com{endpoint}"
    params = {'query': 'email:test@example.com'}
    
    print(f"\nTesting: {url}")
    print(f"Auth header: Basic {encoded[:15]}...")
    
    try:
        response = requests.get(url, headers=headers, params=params, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.history:
            print(f"Redirects: {[r.status_code for r in response.history]}")
            print(f"Final URL: {response.url}")
    except Exception as e:
        print(f"Error: {e}")
