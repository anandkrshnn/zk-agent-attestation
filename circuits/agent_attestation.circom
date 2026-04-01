pragma circom 2.0.0;

/*
 * zk-agent-attestation — Agent Identity Template (v1.0)
 * ZK-SNARK circuit for the PTV protocol.
 * This circuit verifies that an agent's hardware-anchored claims 
 * (model hash and policy fingerprint) match the expected baseline.
 */

template AgentAttestation() {
    // Public Inputs (Baseline values)
    signal input expected_model_hash;
    signal input expected_policy_fingerprint;

    // Private Inputs (Actual measurements from TPM/Enclave)
    signal input actual_model_hash;
    signal input actual_policy_fingerprint;

    // Constraints: Actual inputs MUST match public baseline
    actual_model_hash === expected_model_hash;
    actual_policy_fingerprint === expected_policy_fingerprint;
}

// Instantiate the component
component main {public [expected_model_hash, expected_policy_fingerprint]} = AgentAttestation();
