#!/usr/bin/env python3
"""
zk-agent-attestation — Linux TPM PCR Quote flow (v2.0)
Uses tpm2-tools to generate hardware quotes over selected PCR registers.
Supports persistent AK paths, unique temp file scopes, and robust error handling.
"""

import subprocess
import os
import hashlib
import re
import tempfile
import shutil

class TpmConnectionError(Exception):
    """Raised when the TPM device is missing or inaccessible."""
    pass

class TpmExecutionError(Exception):
    """Raised when a tpm2-tools command fails."""
    pass

class TpmValidationError(Exception):
    """Raised when verification or validation checks fail."""
    pass

class LinuxTpmAttester:
    def __init__(self, tpm_device="/dev/tpmrm0", persistent_ak_ctx=None):
        self.tpm_device = tpm_device
        self.persistent_ak_ctx = persistent_ak_ctx

    def execute_command(self, cmd: list) -> tuple:
        """Helper to run tpm2-tools subprocess commands securely."""
        if not os.path.exists(self.tpm_device) and self.tpm_device != "mock":
            raise TpmConnectionError(f"TPM device node {self.tpm_device} is not accessible.")
            
        try:
            # Set TPM2TOOLS_TCTI environment variable to enforce device-node flow
            env = os.environ.copy()
            env["TPM2TOOLS_TCTI"] = f"device:{self.tpm_device}"
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            raise TpmExecutionError(f"TPM command failed: {' '.join(cmd)}. Error: {e.stderr.strip()}") from e
        except FileNotFoundError:
            raise TpmConnectionError(f"Command not found: {cmd[0]}. Ensure tpm2-tools is installed.")

    def get_ak_pub(self, ak_ctx="ak.ctx", ak_pub="ak.pub") -> str:
        """
        Creates Endorsement Key (EK) and Attestation Key (AK) if they do not exist,
        and returns the SHA-256 hash of the AK public key.
        """
        # If persistent_ak_ctx is provided and exists, use it instead of generating a new one
        active_ak_ctx = self.persistent_ak_ctx or ak_ctx
        
        # If persistent AK context exists, check if public key file is also present
        if self.persistent_ak_ctx and os.path.exists(self.persistent_ak_ctx) and os.path.exists(ak_pub):
            with open(ak_pub, "rb") as f:
                pub_data = f.read()
            return hashlib.sha256(pub_data).hexdigest()

        # Create unique temp directories to prevent collisions during key creation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_ek_ctx = os.path.join(temp_dir, "ek.ctx")
            temp_ak_ctx = os.path.join(temp_dir, "ak.ctx")
            temp_ak_pub = os.path.join(temp_dir, "ak.pub")
            
            # 1. Create EK
            self.execute_command(["tpm2_createek", "-c", temp_ek_ctx])
            
            # 2. Create AK
            self.execute_command(["tpm2_createak", "-C", temp_ek_ctx, "-c", temp_ak_ctx, "-u", temp_ak_pub])
            
            # Save persistent AK if configured
            if self.persistent_ak_ctx:
                shutil.copy(temp_ak_ctx, self.persistent_ak_ctx)
                shutil.copy(temp_ak_pub, ak_pub)
            else:
                shutil.copy(temp_ak_ctx, ak_ctx)
                shutil.copy(temp_ak_pub, ak_pub)

            with open(temp_ak_pub, "rb") as f:
                pub_data = f.read()
            return hashlib.sha256(pub_data).hexdigest()

    def get_pcr_quote(self, pcr_selection="sha256:0,1,2", nonce="", ak_ctx="ak.ctx") -> dict:
        """
        Generates a quote over selected PCR indices with a nonce, parses the resulting message
        and PCR digests, hashes the quote inputs, and returns the attestation structures.
        """
        # Validate inputs
        if not re.match(r"^[a-zA-Z0-9]+:[0-9,]+$", pcr_selection):
            raise ValueError(f"Invalid PCR selection format: {pcr_selection}")
        if nonce and not re.match(r"^[a-fA-F0-9]+$", nonce):
            raise ValueError("Nonce must be a hex string")

        active_ak_ctx = self.persistent_ak_ctx or ak_ctx
        if not os.path.exists(active_ak_ctx):
            raise TpmValidationError(f"Attestation Key context {active_ak_ctx} not found. Run get_ak_pub first.")

        # Execute using a temporary directory to handle message, sig, and PCR dumps safely
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_msg = os.path.join(temp_dir, "quote.msg")
            temp_sig = os.path.join(temp_dir, "quote.sig")
            temp_pcrs = os.path.join(temp_dir, "quote.pcrs")

            cmd = [
                "tpm2_quote",
                "-c", active_ak_ctx,
                "-l", pcr_selection,
                "-q", nonce,
                "-m", temp_msg,
                "-s", temp_sig,
                "-o", temp_pcrs,
                "-g", "sha256"
            ]

            self.execute_command(cmd)

            if not os.path.exists(temp_msg) or not os.path.exists(temp_pcrs):
                raise TpmExecutionError("TPM quote generation failed to output files.")

            with open(temp_msg, "rb") as f:
                msg_bytes = f.read()
            with open(temp_pcrs, "rb") as f:
                pcr_bytes = f.read()

            msg_hash = hashlib.sha256(msg_bytes).hexdigest()
            pcr_hash = hashlib.sha256(pcr_bytes).hexdigest()
            
            # Copy signature out to local context if verification is needed outside the temp scope
            sig_exists = os.path.exists(temp_sig)
            if sig_exists:
                shutil.copy(temp_sig, "quote.sig")
                shutil.copy(temp_msg, "quote.msg")
                shutil.copy(temp_pcrs, "quote.pcrs")

            return {
                "pcr_selection": pcr_selection,
                "nonce": nonce,
                "quote_msg_hash": msg_hash,
                "quote_pcrs_hash": pcr_hash,
                "quote_sig_exists": sig_exists
            }

    def verify_quote(self, ak_pub="ak.pub", quote_msg="quote.msg", quote_sig="quote.sig", quote_pcrs="quote.pcrs", nonce="") -> bool:
        """
        Uses tpm2_checkquote to check that the signature is valid.
        """
        if not os.path.exists(ak_pub) or not os.path.exists(quote_msg) or not os.path.exists(quote_sig):
            raise TpmValidationError("Verification files (ak.pub, quote.msg, quote.sig) not found on disk.")

        cmd = [
            "tpm2_checkquote",
            "-u", ak_pub,
            "-m", quote_msg,
            "-s", quote_sig,
            "-f", quote_pcrs,
            "-q", nonce,
            "-g", "sha256"
        ]
        try:
            self.execute_command(cmd)
            return True
        except TpmExecutionError as e:
            # Distinguish quote verification failure
            raise TpmValidationError(f"TPM quote signature check failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during quote check: {e}")

def compute_golden_pcr_hash(pcr_bin_path: str) -> str:
    """Computes a SHA-256 hash of raw PCR binary data to use as baseline."""
    if not os.path.exists(pcr_bin_path):
        raise FileNotFoundError(f"PCR binary file not found: {pcr_bin_path}")
    with open(pcr_bin_path, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest()
