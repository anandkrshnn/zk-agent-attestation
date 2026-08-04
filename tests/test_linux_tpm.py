#!/usr/bin/env python3
"""
zk-agent-attestation — Linux TPM Attester Unit Tests
Tests the LinuxTpmAttester class using mock subprocess interactions.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add root folder to sys.path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hardware_trust.linux_tpm import (
    LinuxTpmAttester, 
    compute_golden_pcr_hash,
    TpmConnectionError,
    TpmExecutionError,
    TpmValidationError
)

class TestLinuxTpmAttester(unittest.TestCase):
    def setUp(self):
        # Using "mock" as device path to bypass exists checks in execute_command
        self.attester = LinuxTpmAttester(tpm_device="mock")

    @patch("subprocess.run")
    def test_execute_command_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout=" success-stdout \n", stderr="", returncode=0)
        out, err = self.attester.execute_command(["tpm2_pcrread"])
        self.assertEqual(out, "success-stdout")
        self.assertEqual(err, "")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_execute_command_failure(self, mock_run):
        import subprocess
        # Mock CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["tpm2_pcrread"],
            stderr="failed-stderr"
        )
        with self.assertRaises(TpmExecutionError) as ctx:
            self.attester.execute_command(["tpm2_pcrread"])
        self.assertIn("failed-stderr", str(ctx.exception))

    @patch("subprocess.run")
    def test_execute_command_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(TpmConnectionError) as ctx:
            self.attester.execute_command(["invalid_tpm_cmd"])
        self.assertIn("Ensure tpm2-tools is installed", str(ctx.exception))

    @patch("shutil.copy")
    @patch("builtins.open", new_callable=mock_open, read_data=b"mock-ak-pub-data")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_get_ak_pub(self, mock_run, mock_exists, mock_file, mock_copy):
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        ak_hash = self.attester.get_ak_pub(ak_ctx="ak.ctx", ak_pub="ak.pub")
        import hashlib
        expected_hash = hashlib.sha256(b"mock-ak-pub-data").hexdigest()
        self.assertEqual(ak_hash, expected_hash)
        
        # Verify tpm2 tools commands were invoked
        self.assertEqual(mock_run.call_count, 2)
        mock_copy.assert_called()

    @patch("shutil.copy")
    @patch("builtins.open")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_get_pcr_quote(self, mock_run, mock_exists, mock_file, mock_copy):
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        
        # Mock file reads for quote.msg and quote.pcrs
        mock_file.side_effect = [
            mock_open(read_data=b"mock-quote-msg").return_value,
            mock_open(read_data=b"mock-quote-pcrs").return_value
        ]

        quote = self.attester.get_pcr_quote(pcr_selection="sha256:0,1,2", nonce="aabbcc", ak_ctx="ak.ctx")
        
        import hashlib
        expected_msg_hash = hashlib.sha256(b"mock-quote-msg").hexdigest()
        expected_pcrs_hash = hashlib.sha256(b"mock-quote-pcrs").hexdigest()
        
        self.assertEqual(quote["quote_msg_hash"], expected_msg_hash)
        self.assertEqual(quote["quote_pcrs_hash"], expected_pcrs_hash)
        self.assertTrue(quote["quote_sig_exists"])

    def test_get_pcr_quote_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.attester.get_pcr_quote(pcr_selection="invalid")
        with self.assertRaises(ValueError):
            self.attester.get_pcr_quote(nonce="not-hex")

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_verify_quote_success(self, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        is_valid = self.attester.verify_quote(ak_pub="ak.pub", nonce="1234")
        self.assertTrue(is_valid)

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_verify_quote_failure(self, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        
        # Simulating TpmExecutionError to trigger TpmValidationError in verify_quote
        attester_mock = MagicMock()
        attester_mock.execute_command.side_effect = TpmExecutionError("signature mismatch")
        
        with patch.object(self.attester, "execute_command", attester_mock.execute_command):
            with self.assertRaises(TpmValidationError):
                self.attester.verify_quote(ak_pub="ak.pub", nonce="1234")

    @patch("builtins.open", new_callable=mock_open, read_data=b"mock-pcr-binary-data")
    @patch("os.path.exists")
    def test_compute_golden_pcr_hash(self, mock_exists, mock_file):
        mock_exists.return_value = True
        h = compute_golden_pcr_hash("pcr.bin")
        import hashlib
        self.assertEqual(h, hashlib.sha256(b"mock-pcr-binary-data").hexdigest())

if __name__ == "__main__":
    unittest.main()
