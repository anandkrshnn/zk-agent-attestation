pragma circom 2.0.0;

/*
 * zk-agent-attestation — Agent Identity Circuit (v1.1)
 * ZK-SNARK circuit for the Prove-Transform-Verify (PTV) protocol.
 *
 * This circuit verifies that an agent's hardware-anchored claims
 * (model hash and policy fingerprint) match the expected baseline,
 * without revealing the private measurements themselves.
 *
 * Constraints enforce:
 *   actual_model_hash === expected_model_hash
 *   actual_policy_fingerprint === expected_policy_fingerprint
 */

template AgentAttestation() {
    // Public Inputs: Baseline values (known to verifier)
    signal input expected_model_hash;
    signal input expected_policy_fingerprint;

    // Private Inputs: Actual measurements from TPM/Enclave (known only to prover)
    signal input actual_model_hash;
    signal input actual_policy_fingerprint;

    // Intermediate signals to force non-trivial constraint generation
    signal model_diff;
    signal policy_diff;

    model_diff <== actual_model_hash - expected_model_hash;
    policy_diff <== actual_policy_fingerprint - expected_policy_fingerprint;

    // Hard constraints: diff MUST be zero for proof to be valid
    model_diff === 0;
    policy_diff === 0;
}

// Public signals: expected values are visible to the verifier
// Private signals: actual measurements are never revealed
component main {public [expected_model_hash, expected_policy_fingerprint]} = AgentAttestation();
