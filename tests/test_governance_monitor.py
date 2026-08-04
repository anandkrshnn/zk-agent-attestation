#!/usr/bin/env python3
"""
zk-agent-attestation — Integration Tests for Governance Monitoring and Mock Clinical API
"""

import sys
import os
import unittest
import threading
import time
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer

# Add root folder to sys.path to import src and demo modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from demo.governance_monitor import GovernanceHTTPHandler
from demo.pilot_clinical_api import ClinicalHTTPHandler, ACTIVE_ATTESTATION_FILE
import demo.governance_monitor as gov_monitor
import demo.pilot_clinical_api as clinical_api

class TestGovernanceMonitorIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Clear in-memory log stores and delete state file
        gov_monitor.ATTESTATION_LOGS.clear()
        if os.path.exists(ACTIVE_ATTESTATION_FILE):
            os.remove(ACTIVE_ATTESTATION_FILE)

        # 2. Spin up Governance Monitor Server on port 8989
        cls.gov_server = HTTPServer(("localhost", 8989), GovernanceHTTPHandler)
        cls.gov_thread = threading.Thread(target=cls.gov_server.serve_forever, daemon=True)
        cls.gov_thread.start()

        # 3. Spin up Mock Clinical API on port 8980
        cls.clinical_server = HTTPServer(("localhost", 8980), ClinicalHTTPHandler)
        cls.clinical_thread = threading.Thread(target=cls.clinical_server.serve_forever, daemon=True)
        cls.clinical_thread.start()

        # Redirect target URLs for clinical API tests
        clinical_api.MONITOR_URL = "http://localhost:8989/attest"

        # Load valid proof sample generated from compilation scripts
        sample_path = "circuits/poseidon_multi_proof_sample.json"
        if os.path.exists(sample_path):
            with open(sample_path, "r") as f:
                cls.sample_proof_data = json.load(f)
        else:
            # Fallback mock for pure python test isolation if sample is not generated
            cls.sample_proof_data = {
                "proof": {"pi_a": ["0", "0", "0"], "pi_b": [["0", "0"], ["0", "0"], ["0", "0"]], "pi_c": ["0", "0", "0"]},
                "publicSignals": ["0", "0"]
            }

        # Give servers a brief moment to boot up
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.gov_server.shutdown()
        cls.gov_server.server_close()
        cls.clinical_server.shutdown()
        cls.clinical_server.server_close()
        if os.path.exists(ACTIVE_ATTESTATION_FILE):
            os.remove(ACTIVE_ATTESTATION_FILE)

    def test_01_health_checks(self):
        # Test monitor health
        with urllib.request.urlopen("http://localhost:8989/health") as r:
            self.assertEqual(r.getcode(), 200)
            body = json.loads(r.read().decode("utf-8"))
            self.assertEqual(body["status"], "healthy")

    def test_02_diagnose_blocked_before_initialize(self):
        # Test clinical API blocks requests before initialization
        req = urllib.request.Request("http://localhost:8980/diagnose?symptoms=fever")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 403)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("Model attestation not verified", body["reason"])

    def test_03_initialize_success(self):
        # Initialize model with the valid ZK proof payload
        payload = {
            "model_hash": "a8f5e1329c0f456ba178d24b6e5111002",
            "expected_model_hash": "a8f5e1329c0f456ba178d24b6e5111002",
            "policy_hash": "112233445566778899aabbccddeeff00",
            "proof": self.sample_proof_data["proof"],
            "publicSignals": self.sample_proof_data["publicSignals"],
            "latency_ms": 48.5
        }
        req = urllib.request.Request(
            "http://localhost:8980/initialize",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as r:
            self.assertEqual(r.getcode(), 200)
            body = json.loads(r.read().decode("utf-8"))
            self.assertEqual(body["status"], "ATTESTED")
            self.assertIn("proof_id", body)
            proof_id = body["proof_id"]

        # Ensure diagnosis works now
        with urllib.request.urlopen("http://localhost:8980/diagnose?symptoms=cough") as r:
            self.assertEqual(r.getcode(), 200)
            diag_body = json.loads(r.read().decode("utf-8"))
            self.assertEqual(diag_body["attestation_proof_id"], proof_id)
            self.assertEqual(diag_body["attestation_status"], "VERIFIED_HARDWARE_TPM")

    def test_04_initialize_mismatch_fails(self):
        # Initialize with mismatching model hash but valid proof structure (should fail due to mismatch)
        payload = {
            "model_hash": "tampered_model_hash_values_12345678",
            "expected_model_hash": "a8f5e1329c0f456ba178d24b6e5111002",
            "policy_hash": "112233445566778899aabbccddeeff00",
            "proof": self.sample_proof_data["proof"],
            "publicSignals": self.sample_proof_data["publicSignals"],
            "latency_ms": 50.0
        }
        req = urllib.request.Request(
            "http://localhost:8980/initialize",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 403)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body["status"], "REJECTED")

        # Diagnosis should be blocked again after a failed initialization
        req_diag = urllib.request.Request("http://localhost:8980/diagnose?symptoms=fever")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req_diag)
        self.assertEqual(ctx.exception.code, 403)

    def test_05_invalid_proof_rejected(self):
        # Initialize with invalid cryptographic parameters (should fail SnarkJS validation)
        payload = {
            "model_hash": "a8f5e1329c0f456ba178d24b6e5111002",
            "expected_model_hash": "a8f5e1329c0f456ba178d24b6e5111002",
            "policy_hash": "112233445566778899aabbccddeeff00",
            "proof": {"pi_a": ["0", "0", "0"], "pi_b": [["0", "0"], ["0", "0"], ["0", "0"]], "pi_c": ["0", "0", "0"]},
            "publicSignals": ["123", "456"], # Invalid signals
            "latency_ms": 9.2
        }
        req = urllib.request.Request(
            "http://localhost:8980/initialize",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 403)

    def test_06_query_governance_logs(self):
        # Check logs collected by the monitor (from the previous successful/mismatched/failed runs)
        with urllib.request.urlopen("http://localhost:8989/logs") as r:
            self.assertEqual(r.getcode(), 200)
            logs = json.loads(r.read().decode("utf-8"))
            # We expect 2 logged entries (test_03 and test_04). The invalid proof in test_05 was rejected with 422 before logging.
            self.assertEqual(len(logs), 2)

        # Query only model mismatches
        with urllib.request.urlopen("http://localhost:8989/logs?mismatch_only=true") as r:
            mismatched_logs = json.loads(r.read().decode("utf-8"))
            self.assertEqual(len(mismatched_logs), 1)
            self.assertTrue(mismatched_logs[0]["mismatch"])

if __name__ == "__main__":
    unittest.main()
