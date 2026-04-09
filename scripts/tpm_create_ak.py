#!/usr/bin/env python3
"""
Sovereign AI Stack — TPM 2.0 Attestation Key (AK) Generation (v1.0)
Creating the hardware-anchored identity for the PTV protocol.
"""

import os
import subprocess
import json

# =============================================================================
# Configuration
# =============================================================================

TPM_SIMULATOR = os.environ.get("TPM_SIMULATOR", "false").lower() == "true"
OWNER_AUTH = os.environ.get("TPM_OWNER_AUTH", "sovereign_secure_2026")

def log(msg):
    print(f"[TPM-AK] {msg}")

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

def generate_ak():
    log("Starting Sovereign Edge Attestation Key (AK) generation...")
    
    if TPM_SIMULATOR:
        log("⚠️ Running in SIMULATOR mode. No physical hardware required.")

    # 1. Create AK from Primary Storage Key (SRK)
    # The AK is restricted for signing (attestation) only
    log("Creating Attestation Key (AK)...")
    success, output = run_tpm_cmd([
        "tpm2_create", "-C", "primary.ctx", 
        "-c", "ak.ctx", "-G", "rsa2048", 
        "-u", "ak.pub", "-r", "ak.priv", 
        "-a", "restricted|sensitivedataorigin|sign|fixedtpm|fixedparent", 
        "-P", OWNER_AUTH
    ])
    if not success:
        log(f"❌ Failed to create AK: {output}")
        return False

    # 2. Persist AK (Optional, depends on your key management strategy)
    # success, output = run_tpm_cmd(["tpm2_evictcontrol", "-c", "ak.ctx", "0x81010001"])
    # if not success: log(f"⚠️ Failed to persist AK: {output}")

    # 3. Certification (In production, the AK is certified by the EK)
    log("Generating AK certification...")
    success, output = run_tpm_cmd(["tpm2_readpublic", "-c", "ak.ctx", "-o", "ak.pub"])
    if not success: log(f"⚠️ ReadPublic failed: {output}")

    log("✅ Attestation Key (AK) generated successfully.")
    log(f"🔗 AK stored in: ak.ctx (Sovereign Root Identity)")
    return True

if __name__ == "__main__":
    if generate_ak():
        log("🚀 Sovereign Edge Attestation Key (AK) is active.")
    else:
        log("❌ AK generation failed. Sovereign Edge identity is not hardware-bound.")
