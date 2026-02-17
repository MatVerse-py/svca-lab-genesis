import requests
import json
import os
from pathlib import Path

# Zenodo Production API
ZENODO_API_URL = "https://sandbox.zenodo.org/api/deposit/depositions"
# SANDBOX_API_URL = "https://sandbox.zenodo.org/api/deposit/depositions"

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

def load_author_metadata():
    metadata_path = Path(__file__).parent / "AUTHOR_METADATA.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            return json.load(f)
    return None

def create_deposit():
    token = get_token()
    if not token:
        print("❌ Error: ZENODO_ACCESS_TOKEN not found.")
        return None

    author = load_author_metadata()
    if not author:
        print("❌ Error: AUTHOR_METADATA.json not found.")
        return None

    headers = {"Content-Type": "application/json"}
    params = {'access_token': token}
    
    metadata = {
        'metadata': {
            'title': 'SVCA Lab: Executable Science with Cryptographic Verification and Adaptive Physical Identity',
            'upload_type': 'software',
            'description': 'A framework for executable science that bridges physical uniqueness with digital immutability based on the CORE B DAY protocol. Features Ω-SEED primitive, adaptive admissibility algebra (Σ-Ω-Ψ), and real hardware bridge for RP2040.',
            'creators': [{
                'name': author['name'],
                'affiliation': author['affiliation'],
                'orcid': author['orcid']
            }],
            'keywords': ['cryptography', 'PUF', 'reproducibility', 'blockchain', 'RP2040', 'Adaptive Omega'],
            'notes': f"Genesis Artifact included. Author ORCID: {author['orcid']}. MatVerse Research Program (QIG-Σ).",
            'access_right': 'open',
            'license': 'MIT'
        }
    }
    
    try:
        # Step 1: Create the deposition
        response = requests.post(ZENODO_API_URL, params=params, json=metadata, headers=headers)
        response.raise_for_status()
        deposition_id = response.json()['id']
        bucket_url = response.json()['links']['bucket']
        
        print(f"✅ Zenodo Deposition Created. ID: {deposition_id}")
        
        # Step 2: Upload the project tarball
        tarball_path = Path("/home/ubuntu/svca-lab.tar.gz")
        if not tarball_path.exists():
            # Create tarball if it doesn't exist
            os.system(f"cd /home/ubuntu && tar -czf svca-lab.tar.gz svca-lab-genesis")
            
        with open(tarball_path, "rb") as f:
            upload_url = f"{bucket_url}/svca-lab.tar.gz"
            upload_response = requests.put(upload_url, data=f, params=params)
            upload_response.raise_for_status()
            print(f"✅ Project tarball uploaded to Zenodo.")

        # Step 3: Upload the Genesis Artifact
        artifact_dir = Path(__file__).parent / "artifact"
        genesis_files = list(artifact_dir.glob("genesis_*.json"))
        if genesis_files:
            genesis_file = genesis_files[0]
            with open(genesis_file, "rb") as f:
                upload_url = f"{bucket_url}/{genesis_file.name}"
                upload_response = requests.put(upload_url, data=f, params=params)
                upload_response.raise_for_status()
                print(f"✅ Genesis Artifact uploaded to Zenodo.")

        # Step 4: Publish (Optional - usually done manually after review)
        # publish_url = f"{ZENODO_API_URL}/{deposition_id}/actions/publish"
        # publish_response = requests.post(publish_url, params=params)
        # publish_response.raise_for_status()
        # doi = publish_response.json()['doi']
        
        # Get prereserved DOI
        reserved_doi = response.json().get('metadata', {}).get('prereserve_doi', {}).get('doi', 'Pending')
        print(f"📌 Reserved DOI: {reserved_doi}")
        
        return {
            "id": deposition_id,
            "doi": reserved_doi,
            "url": f"https://zenodo.org/deposit/{deposition_id}"
        }
        
    except Exception as e:
        print(f"❌ Zenodo Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    result = create_deposit()
    if result:
        # Save result to a file for later use
        with open("ZENODO_RESULT.json", "w") as f:
            json.dump(result, f, indent=2)
