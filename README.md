# 🔐 zk-agent-attestation

**Hardware-Ready Zero-Knowledge Attestation for AI Agent Identity — PTV Protocol Reference Implementation**

> **Status: Working Research Prototype.** The ZK proof pipeline is fully operational with Poseidon in-circuit hashing and 426 non-linear constraints. This repository implements the Prove–Transform–Verify (PTV) protocol as a reference for AI governance frameworks including Singapore's Model AI Governance Framework and AI Verify.

---

## What is PTV?

Prove–Transform–Verify (PTV) is a zero-knowledge attestation protocol that provides cryptographic proof that an AI agent is running an authorised model and policy — without exposing model weights, proprietary configuration, or sensitive data.

**The core claim:** A verifier can confirm *"this agent is who it claims to be"* with cryptographic attestation — not just API-level trust.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PTV Protocol Flow                     │
├──────────┬──────────────────────────┬───────────────────┤
│  PROVE   │  Agent measures model    │  Software-sim now │
│          │  hash + policy hash      │  TPM/SGX in v2    │
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

## 🏥 Real-World Performance Context

The 58ms round-trip is designed to be **non-intrusive** — attestation runs in the background before a result is surfaced to the end user.

**Clinical Decision Support — Data Flow:**

```
[AI Model Inference]
        │
        ▼
[PTV: Prove — model hash bound to policy hash]   ← ~49ms
        │
        ▼
[PTV: Verify — proof checked against baseline]   ← ~9.2ms
        │
        ▼
[Result surfaced to clinician on screen]         ← doctor sees result AFTER attestation completes
```

> The clinician sees the result only after silent background attestation passes. Zero added latency from the user's perspective. Total attestation overhead: **~58ms** — well within the response window of clinical decision systems (typically 500ms–2s).

**Industrial AI context:** For real-time factory controllers requiring decisions at >100Hz (10ms cycles), PTV attestation is designed as a **session-level** check at model load time, not per-inference. The 58ms overhead is a one-time cost per deployment, not per decision.

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

## 🔒 Security Considerations

### SHA-256 Truncation
Poseidon circuit inputs require field elements within the BN128 scalar field (254-bit). SHA-256 produces 256-bit outputs. The current implementation truncates 2 bits when converting SHA-256 hashes to Poseidon inputs.

**Impact:** The effective collision resistance is reduced from 2^128 (full SHA-256) to approximately 2^126. For a v0.1.0 research prototype operating in non-adversarial attestation environments, this reduction is acceptable. For high-security production deployments, this must be addressed before use.

**Planned resolution (v3):** Full multi-field hashing — the SHA-256 output will be split across multiple Poseidon field inputs, preserving all 256 bits without truncation. This eliminates the collision risk entirely.

**Current mitigation:** Do not use this implementation in adversarial environments where a motivated attacker has the ability to construct crafted model artifacts. Use only in controlled governance and audit workflows.

---

## 🗺️ Path to Hardware Integration

The current implementation uses **software-simulated measurements** — the model hash and policy hash are computed in software, not anchored to physical hardware.

The "Hardware-Ready" designation reflects the protocol's architecture, which is designed from the ground up for hardware binding. The integration path is:

| Version | Hardware Target | Status |
|---|---|---|
| v0.1.0 (current) | Software simulation | ✅ Complete |
| v2.0 | TPM 2.0 (Trusted Platform Module) | 🔬 Research |
| v2.0 | Intel SGX / AMD SEV enclave | 🔬 Research |
| v3.0 | ARM TrustZone (mobile/edge) | 📋 Planned |

**v2 technical approach:** The PROVE stage will delegate model hash measurement to the TPM's PCR (Platform Configuration Register) banks, producing a hardware-signed measurement that replaces the current software hash. The ZK proof pipeline (TRANSFORM + VERIFY) remains unchanged — only the input measurement source changes.

---

## ⚠️ Current Limitations

- Hardware binding is software-simulated in v0.1.0; TPM/SGX integration planned for v2
- Single-threaded proof generation; parallelisation planned for v2
- Poseidon inputs use truncated SHA-256 (254-bit field); full multi-field hashing planned for v3 (see Security Considerations)

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
