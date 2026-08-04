pragma circom 2.0.0;
include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom";

/*
 * zk-agent-attestation - Multi-field Agent Identity Circuit (v2.0 - ptv-v2-multifield)
 *
 * Proves that an agent's private model hash and policy fingerprint (both 256-bit SHA-256
 * digests represented as two 128-bit field elements to prevent truncation) match
 * the expected baseline.
 *
 * Private inputs:
 * - actual_model_hash_chunks[2]: two 128-bit chunks of the model's SHA-256 hash
 * - actual_policy_fingerprint_chunks[2]: two 128-bit chunks of the policy's SHA-256 hash
 *
 * Public inputs:
 * - expected_model_hash_poseidon: Poseidon(actual_model_hash_chunks[0], actual_model_hash_chunks[1])
 * - expected_policy_poseidon: Poseidon(actual_policy_fingerprint_chunks[0], actual_policy_fingerprint_chunks[1])
 */

template AgentAttestationMulti() {
    // Private inputs - 128-bit chunks of the actual measurements
    signal input actual_model_hash_chunks[2];
    signal input actual_policy_fingerprint_chunks[2];

    // Public inputs - expected Poseidon hashes
    signal input expected_model_hash_poseidon;
    signal input expected_policy_poseidon;

    // Hash the private inputs using Poseidon with 2 inputs (sponge)
    component model_hasher = Poseidon(2);
    model_hasher.inputs[0] <== actual_model_hash_chunks[0];
    model_hasher.inputs[1] <== actual_model_hash_chunks[1];

    component policy_hasher = Poseidon(2);
    policy_hasher.inputs[0] <== actual_policy_fingerprint_chunks[0];
    policy_hasher.inputs[1] <== actual_policy_fingerprint_chunks[1];

    // Check hashes match expected public values
    component model_check = IsEqual();
    model_check.in[0] <== model_hasher.out;
    model_check.in[1] <== expected_model_hash_poseidon;
    model_check.out === 1;

    component policy_check = IsEqual();
    policy_check.in[0] <== policy_hasher.out;
    policy_check.in[1] <== expected_policy_poseidon;
    policy_check.out === 1;
}

component main {public [expected_model_hash_poseidon, expected_policy_poseidon]} = AgentAttestationMulti();
