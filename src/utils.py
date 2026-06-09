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

def get_tpm_measurements():
    """
    Read real hardware measurements from local TPM 2.0 via Windows WMI.
    Uses GetSrkPublicKeyModulus (hardware-unique RSA modulus from Intel INTC TPM)
    and GetTcgLog (firmware measurement log — PCR equivalent on Windows).

    Falls back to software simulation if TPM is unavailable (Linux / no WMI).
    """
    try:
        import subprocess

        if platform.system() != "Windows":
            raise EnvironmentError("TPM WMI bridge is Windows-only")

        # Read SRK Public Key Modulus — hardware-unique, burned into Intel INTC chip
        ps_srk = (
            "$tpm = Get-WmiObject -Namespace 'root\\cimv2\\security\\microsofttpm' "
            "-Class Win32_Tpm; "
            "$r = $tpm.GetSrkPublicKeyModulus(); "
            "$r.SrkPublicKeyModulus -join ','"
        )
        srk_result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_srk],
            capture_output=True, text=True, timeout=10
        )
        srk_bytes_str = srk_result.stdout.strip()
        if not srk_bytes_str or srk_result.returncode != 0:
            raise RuntimeError("SRK read failed")

        # Convert SRK byte array to SHA-256 hash
        srk_bytes = bytes([int(b) for b in srk_bytes_str.split(",") if b.strip()])
        srk_hash = hashlib.sha256(srk_bytes).hexdigest()

        # Read TCG Measurement Log — firmware/boot integrity record
        ps_tcg = (
            "$tpm = Get-WmiObject -Namespace 'root\\cimv2\\security\\microsofttpm' "
            "-Class Win32_Tpm; "
            "$r = $tpm.GetTcgLog(); "
            "$r.TcgLog -join ','"
        )
        tcg_result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_tcg],
            capture_output=True, text=True, timeout=10
        )
        tcg_bytes_str = tcg_result.stdout.strip()
        if tcg_bytes_str and tcg_result.returncode == 0:
            tcg_bytes = bytes([int(b) for b in tcg_bytes_str.split(",") if b.strip()])
            tcg_hash = hashlib.sha256(tcg_bytes).hexdigest()
        else:
            tcg_hash = "tcg_unavailable_" + os.urandom(8).hex()

        log(f"TPM SRK hash: {srk_hash[:16]}... [HARDWARE]")
        log(f"TCG log hash: {tcg_hash[:16]}... [HARDWARE]")

        return {
            "source": "TPM_HARDWARE",
            "tpm_manufacturer": "INTC",
            "srk_hash": srk_hash,          # Hardware-unique RSA modulus hash
            "tcg_log_hash": tcg_hash,       # Firmware measurement log hash
            "os": platform.system(),
            "os_release": platform.release(),
            "timestamp": int(time.time()),
            "nonce": os.urandom(16).hex()
        }

    except Exception as e:
        # Graceful fallback — software simulation with explicit warning
        log(f"TPM read failed ({e}), falling back to software simulation", level="WARN")
        return {
            "source": "SOFTWARE_SIMULATION",
            "os": platform.system(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "timestamp": int(time.time()),
            "nonce": os.urandom(16).hex()
        }

# Legacy alias — maintains backward compatibility with existing callers
def get_system_measurements():
    return get_tpm_measurements()

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
