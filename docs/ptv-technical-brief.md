# Prove–Transform–Verify (PTV) Protocol
## Technical Brief for IMDA AI Governance Team

**Author:** Anandakrishnan Damodaran  
**Date:** June 2026  
**Version:** 1.0  
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

**TRANSFORM** — A Groth16 zero-knowledge proof is generated. The proof cryptographically encodes "my private measurements match the public baseline" without revealing the measurements.

**VERIFY** — Any external verifier (regulator, auditor, API gateway) checks the proof against the public baseline in under 5ms. No access to the model is needed.

---

## 3. Performance (Measured on Reference Hardware)

| Operation | Latency | Notes |
|---|---|---|
| Proof generation | ~400ms | One-time per session |
| Proof verification | < 5ms | Per API call |
| Proof size | ~800 bytes | Suitable for API headers |
| Circuit constraints | 2 | Minimal attack surface |

---

## 4. Alignment with Singapore AI Governance Framework

| MOGF Principle | PTV Contribution |
|---|---|
| Accountability | Cryptographic audit trail, non-repudiable |
| Transparency | Public verification key; anyone can verify |
| Explainability | Proof attests to *which* model is running |
| Robustness | Tamper-evident; any model change invalidates proof |
| Fairness | Policy fingerprint ensures governance rules are locked in |

---

## 5. Integration with AI Verify

PTV can operate as a **pre-verification layer** to AI Verify's testing toolkit:

1. Before AI Verify runs its test battery, PTV confirms the model under test is the declared model
2. AI Verify test results are then cryptographically bound to a specific model identity
3. This prevents "model substitution" — passing tests with one model, deploying another

---

## 6. Smart Nation Use Cases

**Healthcare (MOH/IHiS):** Clinical AI systems prove to hospital networks that the deployed model matches the MOH-approved version — without exposing model weights.

**Financial Services (MAS):** Algorithmic trading systems provide regulators a ZK proof of policy compliance without revealing proprietary strategies.

**Industrial (EDB):** Manufacturing AI controllers prove to supply chain partners that they are running the certified safety policy version.

---

## 7. External Validation

- **OECD.AI Catalogue:** Submitted to the OECD.AI Catalogue of Tools & Metrics for Trustworthy AI
- **IETF Internet-Draft:** draft-anandakrishnan-ptv-attested-agent-identity-00 (standardisation track)
- **Reference Implementation:** https://github.com/anandkrshnn/zk-agent-attestation (open source, MIT licence)

---

## 8. Proposed Next Steps with IMDA

1. **Technical Briefing (30 min):** Live demo of the ZK proof pipeline + discussion of AI Verify integration points
2. **Pilot Scope Definition:** Identify one Smart Nation use case for a proof-of-concept integration
3. **MOGF Mapping Workshop:** Map PTV attestation outputs to specific AI Verify test criteria

---

*For technical questions prior to the briefing, please contact: ananda.krishnan@hotmail.com*
