# 🔐 zk-agent-attestation

**Hardware-Anchored Zero-Knowledge Attestation for AI Agent Identity — PTV Protocol Reference Implementation**

> **Status: Working Research Prototype.** The ZK proof pipeline is fully operational with Poseidon in-circuit hashing and 426 non-linear constraints. This repository implements the Prove–Transform–Verify (PTV) protocol as a reference for AI governance frameworks including Singapore's Model AI Governance Framework and AI Verify.

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
│TRANSFORM │  Poseidon hash + Groth16 │  circom + snarkjs │
│          │  ZK proof (426 constraints)  circomlibjs      │
├──────────┼──────────────────────────┼───────────────────┤
│  VERIFY  │  Verifier checks proof   │  ~9ms verify      │
│          │  against public baseline │  (public key)     │
└──────────┴──────────────────────────┴───────────────────┘
```

---

## 📊 Final Benchmark Results (10 runs each, Windows 11, Node.js v24, snarkjs v0.7)

| Config | Circuit | Method | Constraints | Prove Avg | Verify Avg |
|---|---|---|---|---|---|
| 1 | Custom IsEqual | CLI | 4 (--O0) | 435ms | — |
| 2 | circomlib IsEqual | CLI | 0 (optimised away) | 435ms | — |
| 3 | circomlib IsEqual | Library | 0 | 46ms | — |
| **4** | **Poseidon + IsEqual** | **Library** | **426** | **49ms** | **9.2ms** |

> **Config 4 is the production configuration.** Poseidon provides ZK-friendly in-circuit hashing with 426 real non-linear constraints. No `--O0` flag needed. Total attestation round-trip: **~58ms** warm.

---

## 🛠️ Quick Start

### Prerequisites
```bash
npm install snarkjs circomlib circomlibjs
# circom binary: https://github.com/iden3/circom/releases (add to PATH)
```

### Run the full pipeline
```bash
# 1. Compile circuit
circom circuits/agent_attestation.circom --r1cs --wasm --sym -o circuits/
# Expected: 426 non-linear constraints

# 2. Trusted setup (one-time)
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="contributor" -e="random entropy"
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
snarkjs groth16 setup circuits/agent_attestation.r1cs pot12_final.ptau circuit_0000.zkey
snarkjs zkey contribute circuit_0000.zkey circuit_final.zkey --name="ptv-v1" -e="random entropy"
snarkjs zkey export verificationkey circuit_final.zkey verification_key.json

# 3. One-click demo
powershell -ExecutionPolicy Bypass -File demo/run_demo.ps1
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

- **Clinical Decision Support**: Hospital verifies AI model has not been tampered with before accepting diagnosis output
- **Industrial AI**: Factory floor controller proves it is running the certified policy version
- **Financial Services**: Regulatory audit trail without exposing proprietary model weights

---

## ⚠️ Current Limitations

- TPM hardware bridge is research-stage; current implementation uses software-simulated measurements
- Single-threaded proof generation; parallelisation planned for v2
- Poseidon inputs are truncated SHA-256 integers; full multi-field hashing planned for v3

---

## 📜 References

- [OECD.AI Catalogue Submission](https://oecd.ai)
- [IETF Draft: draft-anandakrishnan-ptv-attested-agent-identity-00](https://datatracker.ietf.org/)
- [iden3/circom](https://github.com/iden3/circom)
- [SnarkJS](https://github.com/iden3/snarkjs)
- [circomlib](https://github.com/iden3/circomlib)

---

## 🤝 Contributing

Seeking collaborators with expertise in **Applied Cryptography**, **Hardware Security (TPM/SGX)**, and **AI Governance**. Open an issue or reach out directly.
