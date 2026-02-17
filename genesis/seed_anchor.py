#!/usr/bin/env python3.11
"""
seed_anchor.py - Deterministic Seed Anchoring for MatVerse Node

This script implements the canonical binding of a physical seed to the 
repository state, generating the Ohash (Ontological Hash).

Architecture:
seed -> canonical serialization -> repository digest -> domain-separated hash -> OHASH
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

def get_repo_digest(repo_path: Path) -> str:
    """Computes a deterministic digest of the repository source files."""
    hasher = hashlib.sha3_256()
    # Canonical file ordering
    src_path = repo_path / "src"
    files = sorted(list(src_path.rglob("*.py")))
    
    for file_path in files:
        rel_path = file_path.relative_to(repo_path)
        hasher.update(str(rel_path).encode('utf-8'))
        with open(file_path, "rb") as f:
            hasher.update(f.read())
            
    return hasher.hexdigest()

def generate_ohash(seed: bytes, repo_digest: str, version: str = "MATVERSE_NODE_V1") -> str:
    """Generates a domain-separated Ohash."""
    hasher = hashlib.sha3_256()
    # Domain separation to prevent semantic collisions
    hasher.update(version.encode('utf-8'))
    hasher.update(seed)
    hasher.update(repo_digest.encode('utf-8'))
    return hasher.hexdigest()

def main():
    print("--- MatVerse Seed Anchoring ---")
    
    repo_root = Path(__file__).parent.parent.absolute()
    
    # 1. Acquire Seed (Simulated or Hardware)
    # In a real scenario, this would come from the RP2040 Bridge
    seed = b"MATVERSE_GENESIS_SEED_2026_02_17" 
    
    # 2. Compute Repository Digest
    print("[1/3] Computing repository digest...")
    repo_digest = get_repo_digest(repo_root)
    print(f"✓ Repo Digest: {repo_digest[:16]}...")
    
    # 3. Generate Ohash
    print("[2/3] Generating domain-separated Ohash...")
    ohash = generate_ohash(seed, repo_digest)
    print(f"✓ Ohash: {ohash}")
    
    # 4. Record Results
    print("[3/3] Recording anchoring results...")
    results = {
        "version": "MATVERSE_NODE_V1",
        "ohash": ohash,
        "repo_digest": repo_digest,
        "timestamp": "2026-02-17T00:00:00Z", # Canonical timestamp for genesis
        "methodology": "SHA3-256 with Domain Separation"
    }
    
    output_path = repo_root / "genesis" / "ohash.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"✓ Results saved to {output_path}")
    print("--- Anchoring Complete ---")

if __name__ == "__main__":
    main()
