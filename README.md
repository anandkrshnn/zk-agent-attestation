# 🔐 zk-agent-attestation

**Hardware-Ready Zero-Knowledge Attestation for AI Agent Identity — PTV Protocol Reference Implementation**

> **Status: Working Research Prototype.** The ZK proof pipeline is fully operational with Poseidon in-circuit hashing and 426 non-linear constraints. The PROVE phase reads real hardware measurements from an Intel INTC TPM 2.0 chip via Windows WMI. This repository implements the Prove–Transform–Verify (PTV) protocol as a reference for AI governance frameworks including Singapore's Model AI Governance Framework and AI Verify.

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
│  PROVE   │  Agent measures model    │  Intel INTC TPM   │
│          │  hash + policy hash      │  SRK + TCG log    │
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
| Singapore Model AI Governance Framework (PDPC) v2.0 | Verifiable accountability, explainability layer |
| AI Verify (IMDA, Singapore) v2.0 | Cryptographic evidence for model integrity tests |
| OECD.AI Trustworthy AI | Proposed to OECD.AI Catalogue of Tools & Metrics (under consideration) |
| IETF | Internet-Draft: `draft-anandakrishnan-ptv-attested-agent-identity-00` (individual submission) |

> **Disclaimer:** References to OECD.AI, AI Verify, and IETF are provided solely to contextualise the PTV protocol within existing AI governance and standards ecosystems. This repository is an independent research prototype and does not represent endorsement, certification, adoption, or official validation by OECD, IMDA, PDPC, IETF, or any other standards or regulatory body.
> 
> **IETF Note:** Any referenced Internet-Draft (e.g., `draft-anandakrishnan-ptv-attested-agent-identity-00`) is an individual submission and may change, expire, or be superseded. It does not imply IETF consensus, working group adoption, or standards-track status.

---

## 🔒 Security Considerations

### 2 × 128-bit Multi-Field Hashing (v0.2)
Poseidon circuit inputs require field elements within the BN128 scalar field (~254-bit), while SHA-256 digests produce 256-bit outputs. To preserve the full 256-bit entropy without truncation, PTV v0.2 implements multi-field hashing: the SHA-256 digest is split into **two 128-bit limbs**, which are fed into `Poseidon(2)`.

**Impact:** This design completely preserves the full collision resistance of SHA-256 (2^128) and eliminates the truncation/collision risks present in the previous v0.1.0 prototype.

---

## 🗺️ Path to Hardware Integration

The PROVE phase reads real hardware measurements from a local Intel INTC TPM 2.0 chip via Windows WMI on the development machine. The integration path to production-grade HSM and cloud attestation is:

| Version | Hardware Target | Status |
|---|---|---|
| v0.1.0 (current) | Intel INTC TPM 2.0 — SRK + TCG log via WMI | ✅ Working |
| v2.0 | TPM PCR bank binding (tpm2-tools / Linux) | 🔬 Research |
| v2.0 | Intel SGX / AMD SEV enclave | 🔬 Research |
| v3.0 | ARM TrustZone (mobile/edge) | 📋 Planned |

**v0.1.0 hardware detail:** `GetSrkPublicKeyModulus()` returns the RSA Storage Root Key modulus — a value burned into the Intel INTC chip at manufacture, unique per device, inaccessible to software outside the TPM boundary. `GetTcgLog()` returns the firmware measurement log recording every component loaded at boot. Both values are hashed with SHA-256 and used as inputs to the Poseidon circuit in the PROVE phase.

**v2 technical approach:** The PROVE stage will bind directly to TPM PCR banks via `tpm2-tools`, producing a hardware-signed PCR quote that replaces the current WMI measurement. The ZK proof pipeline (TRANSFORM + VERIFY) remains unchanged.

---

## ⚠️ Current Limitations

- TPM WMI bridge is Windows-only in v0.1.0; Linux tpm2-tools binding planned for v2
- Single-threaded proof generation; parallelisation planned for v2

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
