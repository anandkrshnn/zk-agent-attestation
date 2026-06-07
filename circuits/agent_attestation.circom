pragma circom 2.0.0;
include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom";

/*
 * zk-agent-attestation - Agent Identity Circuit (v2.0)
 *
 * Proves that an agent's private model hash and policy fingerprint
 * match the publicly known expected baseline - using Poseidon hash
 * for ZK-friendly in-circuit hashing.
 *
 * Private inputs: actual_model_hash, actual_policy_fingerprint
 *   (raw field elements from TPM/Enclave measurement)
 *
 * Public inputs: expected_model_hash_poseidon, expected_policy_poseidon
 *   (Poseidon hashes of the approved baseline values)
 *
 * Circuit proves: Poseidon(actual) === expected_poseidon
 * without revealing the actual values.
 */

template AgentAttestation() {
    // Private inputs - actual measurements (never revealed)
    signal input actual_model_hash;
    signal input actual_policy_fingerprint;

    // Public inputs - expected Poseidon hashes of baseline (visible to verifier)
    signal input expected_model_hash_poseidon;
    signal input expected_policy_poseidon;

    // Hash the private inputs using Poseidon (ZK-friendly hash)
    component model_hasher = Poseidon(1);
    model_hasher.inputs[0] <== actual_model_hash;

    component policy_hasher = Poseidon(1);
    policy_hasher.inputs[0] <== actual_policy_fingerprint;

    // Check hashes match expected values
    component model_check = IsEqual();
    model_check.in[0] <== model_hasher.out;
    model_check.in[1] <== expected_model_hash_poseidon;
    model_check.out === 1;

    component policy_check = IsEqual();
    policy_check.in[0] <== policy_hasher.out;
    policy_check.in[1] <== expected_policy_poseidon;
    policy_check.out === 1;
}

component main {public [expected_model_hash_poseidon, expected_policy_poseidon]} = AgentAttestation();
