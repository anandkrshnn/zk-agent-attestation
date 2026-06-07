# 🔐 zk-agent-attestation

**Hardware-Anchored Zero-Knowledge Attestation for AI Agent Identity — PTV Protocol Reference Implementation**

> **Status: Working Research Prototype.** The ZK proof pipeline is fully operational. This repository implements the Prove–Transform–Verify (PTV) protocol as a reference for AI governance frameworks including Singapore's Model AI Governance Framework and AI Verify.

---

## What is PTV?

Prove–Transform–Verify (PTV) is a zero-knowledge attestation protocol that provides cryptographic proof that an AI agent is running an authorised model and policy — without exposing model weights, proprietary configuration, or sensitive data.

**The core claim:** A verifier can confirm *"this agent is who it claims to be"* with mathematical certainty, not just API-level trust.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PTV Protocol Flow                     │
├──────────┬──────────────────────────┬───────────────────┤
│  PROVE   │  Agent measures model    │  TPM/Enclave      │
│          │  hash + policy hash      │  (private)        │
├──────────┼──────────────────────────┼───────────────────┤
│TRANSFORM │  Groth16 ZK proof        │  circom circuit   │
│          │  generated from witness  │  snarkjs          │
├──────────┼──────────────────────────┼───────────────────┤
│  VERIFY  │  Verifier checks proof   │  ~5ms verify      │
│          │  against public baseline │  (public key)     │
└──────────┴──────────────────────────┴───────────────────┘
```

---

## 📊 Benchmarks (Windows 11, Node.js v24, snarkjs v0.7)

| Operation | Time |
|---|---|
| Circuit compilation | < 1s |
| Trusted setup (one-time) | ~3 min |
| Witness generation | < 50ms |
| Groth16 proof generation | ~400ms |
| Proof verification | < 5ms |
| Circuit constraints | 2 (model hash + policy) |

> Proof generation is a one-time per-session cost. Verification at ~5ms is suitable for real-time API gatekeeping.

---

## 🛠️ Quick Start

### Prerequisites
```bash
npm install -g snarkjs
# circom binary: https://github.com/iden3/circom/releases
```

### Run the full pipeline
```bash
# 1. Compile circuit
circom circuits/agent_attestation.circom --r1cs --wasm --sym -o circuits/

# 2. Trusted setup (one-time)
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="contributor" -e="random entropy"
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
snarkjs groth16 setup circuits/agent_attestation.r1cs pot12_final.ptau circuit_0000.zkey
snarkjs zkey contribute circuit_0000.zkey circuit_final.zkey --name="ptv-v1" -e="random entropy"
snarkjs zkey export verificationkey circuit_final.zkey verification_key.json

# 3. Generate input (Node.js to avoid BOM encoding issues on Windows)
node -e "require('fs').writeFileSync('input.json', JSON.stringify({expected_model_hash:'12345678901234567890',expected_policy_fingerprint:'09876543210987654321',actual_model_hash:'12345678901234567890',actual_policy_fingerprint:'09876543210987654321'}))"

# 4. Generate witness
node circuits/agent_attestation_js/generate_witness.js circuits/agent_attestation_js/agent_attestation.wasm input.json witness.wtns

# 5. Prove
snarkjs groth16 prove circuit_final.zkey witness.wtns proof.json public.json

# 6. Verify
snarkjs groth16 verify verification_key.json public.json proof.json
# Expected output: [INFO] snarkJS: OK!
```

---

## 🌏 Relevance to AI Governance

| Framework | PTV Alignment |
|---|---|
| Singapore Model AI Governance Framework | Verifiable accountability, explainability layer |
| AI Verify (IMDA) | Cryptographic evidence for model integrity tests |
| OECD.AI Trustworthy AI | Submitted to OECD.AI Catalogue of Tools & Metrics |
| IETF | Internet-Draft: draft-anandakrishnan-ptv-attested-agent-identity-00 |

---

## 🏥 Smart Nation Use Cases

- **Clinical Decision Support**: Hospital can verify AI model has not been tampered with before accepting diagnosis output
- **Industrial AI**: Factory floor controller proves it is running the certified policy version
- **Financial Services**: Regulatory audit trail without exposing proprietary model weights

---

## ⚠️ Current Limitations

- Hash inputs are field elements (integers); full SHA-256 in-circuit requires Poseidon hash (planned)
- TPM hardware bridge is research-stage; current implementation uses software-simulated measurements
- Single-threaded proof generation; parallelisation planned for v2

---

## 📜 References

- [OECD.AI Catalogue Submission](https://oecd.ai)
- [IETF Draft: draft-anandakrishnan-ptv-attested-agent-identity-00](https://datatracker.ietf.org/)
- [iden3/circom](https://github.com/iden3/circom)
- [SnarkJS](https://github.com/iden3/snarkjs)

---

## 🤝 Contributing

Seeking collaborators with expertise in **Applied Cryptography**, **Hardware Security (TPM/SGX)**, and **AI Governance**. Open an issue or reach out directly.
