import requests
import json
import os
from pathlib import Path

# Zenodo Sandbox API (use https://zenodo.org/api/ for production)
ZENODO_API_URL = "https://sandbox.zenodo.org/api/deposit/depositions"

def get_token():
    # Try to get from environment variable
    token = os.getenv("ZENODO_ACCESS_TOKEN")
    if not token:
        # Try to read from .env file manually if not in env
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("ZENODO_ACCESS_TOKEN="):
                        return line.split("=", 1)[1].strip()
    return token

def create_deposit():
    token = get_token()
    if not token:
        print("❌ Error: ZENODO_ACCESS_TOKEN not found.")
        return None

    headers = {"Content-Type": "application/json"}
    params = {'access_token': token}
    
    metadata = {
        'metadata': {
            'title': 'SVCA Lab: Executable Science with Cryptographic Verification',
            'upload_type': 'software',
            'description': 'A framework for executable science that bridges physical uniqueness with digital immutability based on the CORE B DAY protocol.',
            'creators': [{'name': 'Manus AI', 'affiliation': 'Manus'}],
            'keywords': ['cryptography', 'PUF', 'reproducibility', 'blockchain'],
            'notes': 'Genesis Artifact included.'
        }
    }
    
    try:
        # In a real scenario, we would call the API
        # response = requests.post(ZENODO_API_URL, params=params, json=metadata)
        # response.raise_for_status()
        # deposition_id = response.json()['id']
        
        print("✅ Zenodo Deposit Prepared (Simulated with Token Security)")
        print(f"Title: {metadata['metadata']['title']}")
        print(f"Token identified: {token[:4]}...{token[-4:]}")
        return "123456"
    except Exception as e:
        print(f"❌ Zenodo Error: {e}")
        return None

if __name__ == "__main__":
    create_deposit()
