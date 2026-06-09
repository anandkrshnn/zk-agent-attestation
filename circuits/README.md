# Circuit Documentation — agent_attestation.circom

## Overview

The `agent_attestation.circom` circuit is the core of the PTV TRANSFORM phase. It proves, in zero knowledge, that an AI agent's model hash and policy fingerprint match an expected baseline — without revealing the actual hash values to the verifier.

---

## Circuit File

```
circuits/agent_attestation.circom
```

**Constraint count:** 426 non-linear constraints  
**Hash function:** Poseidon (ZK-friendly, iden3/circomlib)  
**Proof system:** Groth16 (snarkjs)  
**Curve:** BN128 (alt_bn128)  

---

## Inputs and Outputs

### Private Inputs (never revealed to verifier)

| Signal | Type | Description |
|---|---|---|
| `model_hash` | field element | SHA-256 of model weights, truncated to 254-bit BN128 field |
| `policy_hash` | field element | SHA-256 of policy config file, truncated to 254-bit BN128 field |

### Public Inputs (visible to verifier)

| Signal | Type | Description |
|---|---|---|
| `expected_model_hash` | field element | Authorised baseline model hash (published by governance authority) |
| `expected_policy_hash` | field element | Authorised baseline policy hash (published by governance authority) |

### Output

The circuit produces no explicit output signal. A valid proof asserts that:

```
Poseidon(model_hash) == expected_model_hash
Poseidon(policy_hash) == expected_policy_hash
```

If either condition fails, no valid proof can be generated.

---

## Constraint Breakdown

| Component | Constraints | Purpose |
|---|---|---|
| Poseidon hash (model) | ~213 | In-circuit hash of model_hash signal |
| Poseidon hash (policy) | ~213 | In-circuit hash of policy_hash signal |
| IsEqual (model) | ~0 | Equality check (optimised away by compiler) |
| IsEqual (policy) | ~0 | Equality check (optimised away by compiler) |
| **Total** | **426** | |

Note: IsEqual constraints are optimised to 0 by the circom compiler — the equality is enforced algebraically within the Poseidon constraint system itself.

---

## SHA-256 Truncation

SHA-256 produces 256-bit outputs. The BN128 scalar field is 254 bits (prime order r ≈ 2^254). When converting a SHA-256 hash to a circuit input, the top 2 bits are discarded.

**Impact:** Collision resistance reduces from 2^128 to approximately 2^126. See `docs/trusted-setup.md` and the Security Considerations section of the README for full details and the v3 resolution plan.

---

## Test Cases

### Happy Path (currently implemented)
- Model hash matches expected baseline → proof generated, verification passes ✅
- Policy hash matches expected baseline → proof generated, verification passes ✅

### Negative Test Cases (planned for v2)

| Test | Expected Behaviour |
|---|---|
| model_hash ≠ expected_model_hash | Witness generation fails — no proof produced |
| policy_hash ≠ expected_policy_hash | Witness generation fails — no proof produced |
| Both hashes wrong | Witness generation fails |
| Tampered proof submitted to verifier | Verification returns false |
| Replay attack (old valid proof) | Verifier must check timestamp binding (v2 feature) |

The negative test cases confirm that the circuit **cannot** produce a valid proof for an unauthorised model — which is the core security property of PTV.

---

## Compile and Test

```bash
# Compile
circom circuits/agent_attestation.circom --r1cs --wasm --sym -o circuits/

# Verify constraint count
snarkjs r1cs info circuits/agent_attestation.r1cs
# Expected: 426 non-linear constraints

# Generate witness for happy path
node circuits/agent_attestation_js/generate_witness.js \
  circuits/agent_attestation_js/agent_attestation.wasm \
  input.json witness.wtns

# Generate proof
snarkjs groth16 prove circuit_final.zkey witness.wtns proof.json public.json

# Verify
snarkjs groth16 verify verification_key.json public.json proof.json
# Expected: OK
```

---

## v2 Planned Extensions

- **Timestamp binding:** Add `nonce` and `timestamp` as public inputs to prevent proof replay attacks
- **Multi-field hashing:** Split SHA-256 output across two field elements to preserve all 256 bits
- **PCR binding:** Add TPM PCR quote as a third private input, binding proof to physical hardware state
