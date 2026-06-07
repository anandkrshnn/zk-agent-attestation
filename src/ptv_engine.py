"""PTV Engine - bridges Python to the Node.js ZK proof pipeline."""
import subprocess
import json
import time
import hashlib
from pathlib import Path

ROOT = Path(__file__).parent.parent


def _hash_to_field(value: str) -> str:
    """Convert a string to a field element (truncated SHA-256 integer)."""
    h = hashlib.sha256(value.encode()).hexdigest()
    return str(int(h[:16], 16))  # 64-bit integer, safely within BN128 field


def run_ptv_attestation(model_id: str, policy_id: str) -> dict:
    """
    Run the full PTV attestation pipeline.

    Args:
        model_id: Model identifier string (e.g. 'clinical_model_v2')
        policy_id: Policy identifier string (e.g. 'moh_policy_v1')

    Returns:
        dict with keys: valid, prove_ms, verify_ms, proof_hash, error
    """
    try:
        # Convert model/policy strings to field elements
        model_hash = _hash_to_field(model_id)
        policy_hash = _hash_to_field(policy_id)

        # Write input.json
        input_data = {
            "actual_model_hash": model_hash,
            "actual_policy_fingerprint": policy_hash,
            "expected_model_hash_poseidon": "__compute__",
            "expected_policy_poseidon": "__compute__"
        }
        input_path = ROOT / "input.json"
        input_path.write_text(json.dumps(input_data))

        # Call the Node.js prove+verify script
        start = time.time()
        result = subprocess.run(
            ["node", "demo/prove_and_verify.js"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        total_ms = (time.time() - start) * 1000

        if result.returncode != 0:
            return {"valid": False, "error": result.stderr, "prove_ms": 0, "verify_ms": 0}

        # Parse output
        output = result.stdout.strip().splitlines()
        parsed = {}
        for line in output:
            if '=' in line:
                k, v = line.split('=', 1)
                parsed[k] = v

        return {
            "valid": parsed.get('VALID', 'false').lower() == 'true',
            "prove_ms": float(parsed.get('PROVE_AVG', 0)),
            "verify_ms": float(parsed.get('VERIFY_AVG', 0)),
            "prove_min_ms": float(parsed.get('PROVE_MIN', 0)),
            "total_ms": round(total_ms, 1),
            "error": None
        }

    except subprocess.TimeoutExpired:
        return {"valid": False, "error": "Proof generation timed out", "prove_ms": 0, "verify_ms": 0}
    except Exception as e:
        return {"valid": False, "error": str(e), "prove_ms": 0, "verify_ms": 0}
