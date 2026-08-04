#!/usr/bin/env python3
"""
zk-agent-attestation — Mock Clinical API Pilot (v2.0)
Simulates a Clinical Decision Support system that blocks decisions until PTV checks pass.
Enforces real SnarkJS verification on initialization and persists verification state.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import time
import os
import hashlib

# Note: This API acts as the verification and gating layer. 
# Proof generation is performed separately in the JS bridge / TPM path.
ACTIVE_ATTESTATION_FILE = "demo/active_attestation.json"
MONITOR_URL = "http://localhost:8080/attest"
# DEMO ONLY: Rotate and inject via environment variables in production
API_TOKEN = "ptv_gov_secret_token_2026"

def get_attested_state() -> dict:
    """Read persisted attestation record from file."""
    if os.path.exists(ACTIVE_ATTESTATION_FILE):
        try:
            with open(ACTIVE_ATTESTATION_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def set_attested_state(data: dict):
    """Write attestation record to file to ensure durability."""
    try:
        os.makedirs(os.path.dirname(ACTIVE_ATTESTATION_FILE), exist_ok=True)
        with open(ACTIVE_ATTESTATION_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def clear_attested_state():
    """Remove persisted attestation file."""
    if os.path.exists(ACTIVE_ATTESTATION_FILE):
        try:
            os.remove(ACTIVE_ATTESTATION_FILE)
        except Exception:
            pass

class ClinicalHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/initialize":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode("utf-8"))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
                return

            proof = payload.get("proof")
            public_signals = payload.get("publicSignals")
            model_hash = payload.get("model_hash", "a8f5e1329c0f456ba178d24b6e5111002")
            policy_hash = payload.get("policy_hash", "112233445566778899aabbccddeeff00")
            expected_model = payload.get("expected_model_hash", model_hash)

            if not proof or not public_signals:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing proof or publicSignals in payload"}).encode("utf-8"))
                return

            # Construct the attestation payload for the monitor
            proof_id = "PROOF-" + hashlib.sha256(json.dumps(proof).encode()).hexdigest()[:8].upper()
            attestation_data = {
                "timestamp": int(time.time()),
                "model_hash": model_hash,
                "expected_model_hash": expected_model,
                "policy_hash": policy_hash,
                "hardware_digest": "TPM-PCR-AK-DIGEST-MOCK-2026",
                "proof_id": proof_id,
                "proof": proof,
                "publicSignals": public_signals,
                "latency_ms": payload.get("latency_ms", 58.0)
            }

            # Forward to Governance Monitor to perform cryptographic checks
            verified = False
            mismatch_detected = True
            try:
                req = urllib.request.Request(
                    MONITOR_URL,
                    data=json.dumps(attestation_data).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "X-PTV-Token": API_TOKEN
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    verified = res_body.get("verified", False)
                    mismatch_detected = res_body.get("mismatch_detected", True)
            except Exception as e:
                # If monitor service is unavailable or rejected verification, block initialization
                verified = False

            if verified and not mismatch_detected:
                set_attested_state(attestation_data)
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "status": "ATTESTED",
                    "message": "Model loaded and verified under MOH Policy rules.",
                    "proof_id": proof_id
                }).encode("utf-8"))
            else:
                clear_attested_state()
                self._set_headers(403)
                self.wfile.write(json.dumps({
                    "status": "REJECTED",
                    "error": "Cryptographic attestation failed or model weight mismatch detected.",
                    "proof_id": proof_id
                }).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/diagnose":
            attestation_record = get_attested_state()
            if not attestation_record:
                self._set_headers(403)
                self.wfile.write(json.dumps({
                    "error": "Access Blocked",
                    "reason": "Model attestation not verified. Request blocked under MOH Policy guidelines."
                }).encode("utf-8"))
                return

            # Simulate decision and attach proof record
            symptoms = urllib.parse.parse_qs(parsed_url.query).get("symptoms", ["cough"])[0]
            
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "decision": f"Simulated clinical recommendation for symptoms: {symptoms}",
                "attestation_proof_id": attestation_record.get("proof_id"),
                "attestation_status": "VERIFIED_HARDWARE_TPM",
                "timestamp": int(time.time())
            }).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))

def start_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ClinicalHTTPHandler)
    print(f"[*] Starting Mock Clinical API on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    start_server(port)
