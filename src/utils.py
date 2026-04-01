#!/usr/bin/env python3
"""
zk-agent-attestation — Common Utilities (v1.0)
Cryptographic and measurement helpers for the PTV protocol.
"""

import hashlib
import json
import os
import platform
import time

def log(msg, level="INFO"):
    """Localized logging for the PTV stack"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def calculate_sha256(data: str) -> str:
    """Calculate the SHA-256 hash of a string"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def get_system_measurements():
    """
    Collect basic hardware/OS claims for the 'Prove' phase.
    In production, this would interface with a TPM 2.0 or Secure Enclave.
    """
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "timestamp": int(time.time()),
        "nonce": os.urandom(16).hex()
    }

def save_json(data, filepath):
    """Save a dictionary to a JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath):
    """Load a dictionary from a JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None
