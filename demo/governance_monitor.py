#!/usr/bin/env python3
"""
zk-agent-attestation — PTV Governance & Monitoring Service (v2.0)
Lightweight HTTP server to ingest and query PTV session attestation logs.
Enforces real SnarkJS Groth16 verification and header-based authorization.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import subprocess
import tempfile
import os

# Memory store for logs
ATTESTATION_LOGS = []
# DEMO ONLY: Rotate and inject via environment variables in production
API_TOKEN = "ptv_gov_secret_token_2026"

class GovernanceHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default server logs for cleaner console print
        pass

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-PTV-Token")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy"}).encode("utf-8"))
            return

        elif path == "/logs":
            # Apply filters
            filtered_logs = ATTESTATION_LOGS
            
            # Filter by failed verification
            if "failed_only" in query_params:
                val = query_params["failed_only"][0].lower() == "true"
                if val:
                    filtered_logs = [log for log in filtered_logs if not log.get("verified", False)]
            
            # Filter by model/policy mismatch
            if "mismatch_only" in query_params:
                val = query_params["mismatch_only"][0].lower() == "true"
                if val:
                    filtered_logs = [log for log in filtered_logs if log.get("mismatch", False)]

            self._set_headers(200)
            self.wfile.write(json.dumps(filtered_logs).encode("utf-8"))
            return

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/attest":
            # 1. Enforce API Token Authorization
            token = self.headers.get("X-PTV-Token")
            if token != API_TOKEN:
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Unauthorized: Invalid or missing X-PTV-Token"}).encode("utf-8"))
                return

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode("utf-8"))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
                return

            # Required fields validation
            required_fields = ["timestamp", "model_hash", "policy_hash", "hardware_digest", "proof", "publicSignals", "latency_ms"]
            for field in required_fields:
                if field not in payload:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": f"Missing required field: {field}"}).encode("utf-8"))
                    return

            # 2. Cryptographically Verify the Proof out-of-band
            verified = False
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
                temp_filename = f.name
                json.dump({
                    "proof": payload["proof"],
                    "publicSignals": payload["publicSignals"]
                }, f)

            try:
                result = subprocess.run(
                    ["node", "scripts/verify_proof.js", temp_filename],
                    capture_output=True, text=True, timeout=15
                )
                verified = (result.returncode == 0 and "SUCCESS" in result.stdout)
            except Exception as e:
                verified = False
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

            if not verified:
                self._set_headers(422)
                self.wfile.write(json.dumps({"error": "Invalid Cryptographic ZK Proof"}).encode("utf-8"))
                return

            # Check for mismatch between model hash and expected baseline model hash
            actual_model = payload["model_hash"]
            expected_model = payload.get("expected_model_hash", actual_model)
            payload["mismatch"] = actual_model != expected_model
            payload["verified"] = verified

            ATTESTATION_LOGS.append(payload)

            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "logged", "verified": True, "mismatch_detected": payload["mismatch"]}).encode("utf-8"))
            return

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))

def start_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, GovernanceHTTPHandler)
    print(f"[*] Starting PTV Governance Monitor on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    start_server(port)
