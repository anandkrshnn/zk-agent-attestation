# Prove–Transform–Verify (PTV) Protocol
## Technical Brief for IMDA AI Governance Team

**Author:** Anandakrishnan Damodaran  
**Date:** June 2026  
**Version:** 2.0  
**Reference:** IMDA Case 00651089

---

## 1. The Problem PTV Solves

Current AI governance frameworks (including AI Verify) rely on **self-reported** or **API-level** trust: an organisation declares which model they are running and what policies govern it. There is no cryptographic mechanism to verify these claims are true at runtime.

PTV answers one question with mathematical certainty:

> *"Is this AI agent actually running the model and policy it claims to be running — without revealing the model itself?"*

---

## 2. Protocol Overview

PTV has three phases:

**PROVE** — The agent measures its own model hash and policy fingerprint inside a hardware-secure boundary (TPM chip or trusted execution environment). These measurements are private.

**TRANSFORM** — Private measurements are hashed using **Poseidon** (a ZK-friendly hash function) inside the circuit. A Groth16 zero-knowledge proof is generated encoding "my Poseidon-hashed measurements match the public baseline" — without revealing the measurements.

**VERIFY** — Any external verifier (regulator, auditor, API gateway) checks the proof against the public baseline in ~9ms. No access to the model is needed.

---

## 3. Circuit Design

The circuit uses circomlib's production-grade components:
- **Poseidon hash** (ZK-friendly, replaces SHA-256 in-circuit)
- **IsEqual constraint** (enforces hash match)
- **426 non-linear constraints** (no compiler workarounds)
- **No `--O0` flag** (full optimiser enabled)

Private inputs (model hash, policy fingerprint) are never exposed. The verifier only sees the expected Poseidon hashes and the proof.

---

## 4. Verified Performance Benchmarks

All results measured on Windows 11, Node.js v24, snarkjs v0.7, circomlib v2.0.5.

| Config | Circuit | Method | Constraints | Prove Avg | Verify Avg |
|---|---|---|---|---|---|
| 1 | Custom IsEqual | CLI | 4 (--O0) | 435ms | — |
| 2 | circomlib IsEqual | CLI | 0 | 435ms | — |
| 3 | circomlib IsEqual | Library | 0 | 46ms | — |
| **4** | **Poseidon + IsEqual** | **Library** | **426** | **49ms** | **9.2ms** |

**Key findings:**
- CLI overhead (~410ms) is Node.js startup, unrelated to cryptography
- Production library mode with real Poseidon hashing: **49ms prove, 9ms verify**
- Total attestation round-trip: **~58ms warm**
- Verification cost is constant regardless of proof complexity

---

## 5. Alignment with Singapore AI Governance Framework

| MOGF Principle | PTV Contribution |
|---|---|
| Accountability | Cryptographic audit trail, non-repudiable |
| Transparency | Public verification key; anyone can verify |
| Explainability | Proof attests to *which* model is running |
| Robustness | Tamper-evident; any model change invalidates proof |
| Fairness | Policy fingerprint ensures governance rules are locked in |

---

## 6. Integration with AI Verify

PTV operates as a **pre-verification layer** to AI Verify's testing toolkit:

1. Before AI Verify runs its test battery, PTV confirms the model under test is the declared model
2. AI Verify test results are cryptographically bound to a specific model identity
3. This prevents "model substitution" — passing tests with one model, deploying another
4. The `verification_key.json` can be published alongside AI Verify reports as cryptographic evidence

---

## 7. Smart Nation Use Cases

**Healthcare (MOH/IHiS):** Clinical AI systems prove to hospital networks that the deployed model matches the MOH-approved version. Attestation adds ~58ms to session initialisation — imperceptible to users.

**Financial Services (MAS):** Algorithmic trading systems provide regulators a ZK proof of policy compliance without revealing proprietary strategies.

**Industrial (EDB):** Manufacturing AI controllers prove to supply chain partners that they are running the certified safety policy version.

---

## 8. External Validation

- **OECD.AI Catalogue:** Proposed to the OECD.AI Catalogue of Tools & Metrics for Trustworthy AI (under consideration)
- **IETF Internet-Draft:** `draft-anandakrishnan-ptv-attested-agent-identity-00` (individual submission)
- **Reference Implementation:** https://github.com/anandkrshnn/zk-agent-attestation (open source, MIT licence)

> **Disclaimer:** References to OECD.AI, AI Verify, and IETF are provided solely to contextualise the PTV protocol within existing AI governance and standards ecosystems. This document is an independent technical overview and does not represent endorsement, certification, adoption, or validation by OECD, IMDA, PDPC, IETF, or any other standards or regulatory body.

---

## 9. Proposed Next Steps with IMDA

1. **Technical Briefing (30 min):** Live demo of the ZK proof pipeline + discussion of AI Verify integration points
2. **Pilot Scope Definition:** Identify one Smart Nation use case for a proof-of-concept integration
3. **MOGF Mapping Workshop:** Map PTV attestation outputs to specific AI Verify test criteria

---

*For technical questions prior to the briefing, please contact: ananda.krishnan@hotmail.com*
