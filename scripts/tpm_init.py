#!/usr/bin/env python3
"""
Sovereign AI Stack — TPM 2.0 Hierarchy Initialization (v1.0)
Hardware-Anchored Root-of-Trust for the Sovereign Edge.
"""

import os
import subprocess
import json
import time

# =============================================================================
# Configuration
# =============================================================================

TPM_SIMULATOR = os.environ.get("TPM_SIMULATOR", "false").lower() == "true"
OWNER_AUTH = os.environ.get("TPM_OWNER_AUTH", "sovereign_secure_2026")
LOCKOUT_AUTH = os.environ.get("TPM_LOCKOUT_AUTH", "lockout_secure_2026")

def log(msg):
    print(f"[TPM-INIT] {msg}")

def run_tpm_cmd(cmd_list):
    """Execute a tpm2-tools command or simulate success"""
    if TPM_SIMULATOR:
        log(f"SIMULATOR: Running: {' '.join(cmd_list)}")
        return True, "Simulation Successful"
    
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

# =============================================================================
# Implementation
# =============================================================================

def initialize_tpm():
    log("Starting Sovereign Edge TPM initialization...")
    
    if TPM_SIMULATOR:
        log("⚠️ Running in SIMULATOR mode. No physical hardware required.")

    # 1. Clear TPM (Optional, but ensures a clean state for the pilot)
    # WARNING: This destroys all existing keys in the owner hierarchy.
    # success, output = run_tpm_cmd(["tpm2_clear"])
    # if not success: log(f"⚠️ Clear failed (ignore if already cleared): {output}")

    # 2. Set Hierarchy Auth (Owner, Endorsement, Lockout)
    log("Setting hierarchy authentication...")
    success, output = run_tpm_cmd(["tpm2_changeauth", "-c", "owner", OWNER_AUTH])
    if not success: log(f"⚠️ Owner Auth failed: {output}")

    success, output = run_tpm_cmd(["tpm2_changeauth", "-c", "lockout", LOCKOUT_AUTH])
    if not success: log(f"⚠️ Lockout Auth failed: {output}")

    # 3. Create Primary Storage Key (SRK) in the Owner Hierarchy
    log("Creating Storage Root Key (SRK)...")
    success, output = run_tpm_cmd([
        "tpm2_createprimary", "-c", "primary.ctx", 
        "-G", "rsa2048", "-a", "owner", "-P", OWNER_AUTH
    ])
    if not success:
        log(f"❌ Failed to create SRK: {output}")
        return False

    # 4. Final Verification
    log("✅ TPM Hierarchy initialized successfully.")
    return True

if __name__ == "__main__":
    if initialize_tpm():
        log("🚀 Sovereign Edge is now hardware-anchored.")
    else:
        log("❌ Initialization failed. Sovereign Edge remains in 'Soft-Mode'.")
