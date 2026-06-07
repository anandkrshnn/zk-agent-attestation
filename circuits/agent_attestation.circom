pragma circom 2.0.0;

template IsEqual() {
    signal input in[2];
    signal output out;
    signal diff;
    diff <== in[1] - in[0];
    out <-- (diff == 0) ? 1 : 0;
    out * diff === 0;
    out * (out - 1) === 0;
}

template AgentAttestation() {
    signal input expected_model_hash;
    signal input expected_policy_fingerprint;
    signal input actual_model_hash;
    signal input actual_policy_fingerprint;

    component model_check = IsEqual();
    model_check.in[0] <== expected_model_hash;
    model_check.in[1] <== actual_model_hash;
    model_check.out === 1;

    component policy_check = IsEqual();
    policy_check.in[0] <== expected_policy_fingerprint;
    policy_check.in[1] <== actual_policy_fingerprint;
    policy_check.out === 1;
}

component main {public [expected_model_hash, expected_policy_fingerprint]} = AgentAttestation();