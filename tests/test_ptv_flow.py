#!/usr/bin/env python3
"""
zk-agent-attestation — PTV Flow Unit Test (v1.0)
Validating the end-to-end Prove-Transform-Verify logic.
"""

import sys
import os
import unittest
import hashlib

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

    def test_lossless_chunking(self):
        """Verify that split_sha256_to_chunks is lossless and converts back to the original SHA-256"""
        from src.utils import split_sha256_to_chunks
        
        # Test case: a random SHA-256 hex string
        test_hex = "a8f5e1329c0f456ba178d24b6e5111002233445566778899aabbccddeeff0011"
        chunks = split_sha256_to_chunks(test_hex)
        
        # Reconstruct the hex string from the decimal chunk strings
        chunk0_val = int(chunks[0])
        chunk1_val = int(chunks[1])
        
        # Format back to 32-char lowercase hex, padding with leading zeros if necessary
        hex0 = f"{chunk0_val:032x}"
        hex1 = f"{chunk1_val:032x}"
        reconstructed_hex = hex0 + hex1
        
        self.assertEqual(reconstructed_hex, test_hex)
        
        # Test with an arbitrary string (should hash and then split losslessly relative to its hash)
        input_str = "some_random_input_data_2026"
        expected_hash = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
        chunks2 = split_sha256_to_chunks(input_str)
        reconstructed_hex2 = f"{int(chunks2[0]):032x}{int(chunks2[1]):032x}"
        self.assertEqual(reconstructed_hex2, expected_hash)

    def test_real_multi_field_attestation_success(self):
        """Test real ZK proof generation and verification with matching baseline inputs"""
        from src.ptv_engine import run_ptv_attestation
        
        model = "a8f5e1329c0f456ba178d24b6e5111002233445566778899aabbccddeeff0011"
        policy = "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00"
        
        res = run_ptv_attestation(model, policy)
        self.assertIsNone(res.get("error"))
        self.assertTrue(res.get("valid"))
        self.assertGreater(res.get("prove_ms", 0), 0)
        self.assertGreater(res.get("verify_ms", 0), 0)

    def test_real_multi_field_attestation_mismatch_rejected(self):
        """Test real ZK proof rejection when model weights mismatch expected baseline"""
        from src.ptv_engine import run_ptv_attestation
        
        # Mismatching model
        model = "wrong_model_weights_hex_hash_here_1234567890abcdef"
        policy = "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00"
        
        res = run_ptv_attestation(model, policy)
        self.assertFalse(res.get("valid"))

if __name__ == "__main__":
    unittest.main()

