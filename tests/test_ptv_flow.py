#!/usr/bin/env python3
"""
zk-agent-attestation — PTV Flow Unit Test (v1.0)
Validating the end-to-end Prove-Transform-Verify logic.
"""

import sys
import os
import unittest

# Add root folder to sys.path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.prove import collect_claims, generate_proof
from src.verify import verify_proof

class TestPTVFlow(unittest.TestCase):
    """Basic integration test for the PTV protocol"""

    def test_full_ptv_lifecycle(self):
        """Testing the full flow: Collect -> Generate -> Verify"""
        model = "Llama-Test"
        policy = "config/test_policy.yaml"
        
        # 1. Prove
        claims = collect_claims(model, policy)
        self.assertIn("model_hash", claims)
        self.assertEqual(claims["status"], "ATTESTED")
        
        # 2. Transform
        proof = generate_proof(claims)
        self.assertEqual(proof["protocol"], "Groth16")
        
        # 3. Verify
        expected_signals = [claims["model_hash"], claims["policy_fingerprint"]]
        is_valid = verify_proof(proof, expected_signals)
        self.assertTrue(is_valid)

    def test_verification_failure(self):
        """Testing verification failure on signal mismatch"""
        model = "Llama-Test"
        policy = "config/test_policy.yaml"
        
        claims = collect_claims(model, policy)
        proof = generate_proof(claims)
        
        # Tampered signals
        tampered_signals = ["WRONG_HASH", "WRONG_POLICY"]
        is_valid = verify_proof(proof, tampered_signals)
        self.assertFalse(is_valid)

if __name__ == "__main__":
    unittest.main()
