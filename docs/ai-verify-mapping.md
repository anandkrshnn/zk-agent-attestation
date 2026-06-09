# AI Verify Governance Mapping — PTV Protocol

## Overview

This document maps the PTV (Prove–Transform–Verify) protocol to specific principles and testing areas of the **AI Verify Framework** published by IMDA (Infocomm Media Development Authority, Singapore) and the **Singapore Model AI Governance Framework (MAIGF)**.

AI Verify tests AI systems against 11 governance principles. PTV directly addresses **4 of these principles** with cryptographic evidence — not self-attestation or documentation-only claims.

---

## Mapping Table

| AI Verify Principle | Principle Description | How PTV Addresses It | Evidence Type |
|---|---|---|---|
| **Principle 4 — Explainability** | AI systems should be able to explain decisions | PTV proves *which model* produced a decision, creating an immutable audit trail | ZK proof + public verification key |
| **Principle 6 — Robustness** | AI systems should perform reliably and securely | PTV detects any modification to model weights (hash mismatch → proof fails) | Poseidon circuit constraint failure |
| **Principle 8 — Accountability** | There should be mechanisms to ensure responsibility | PTV creates a cryptographic record linking agent output to a specific model version and policy | Handshake ID + proof transcript |
| **Principle 9 — Human Oversight** | Humans should maintain oversight of AI systems | PTV enables a verifier (human or system) to check agent identity before accepting output | Verifier role in PTV protocol |

---

## Detailed Mapping

### Principle 4 — Explainability

**AI Verify test area:** Transparency of AI decision-making process.

**PTV contribution:**  
Without PTV, a downstream system receiving AI output has no way to verify *which model version* or *which policy* produced that output. With PTV, the verifier holds a cryptographic proof binding the output to a specific `model_hash` and `policy_fingerprint`. This is a stronger form of explainability than logging — it is mathematically unforgeable.

**Applicable to:**
- Clinical Decision Support: Hospital can prove which model version issued a diagnosis recommendation
- Financial Services: Regulator can verify which model version made a credit decision, without accessing model weights

---

### Principle 6 — Robustness

**AI Verify test area:** Security and resilience against adversarial inputs and tampering.

**PTV contribution:**  
If an attacker modifies model weights (even a single parameter), the `model_hash` changes. The Poseidon circuit will fail to generate a valid proof for the modified hash against the authorised baseline. The verifier rejects the agent. This is a **tamper-evident seal** at the model level.

**Constraint mechanism:** 426 non-linear Poseidon constraints enforce that the private `model_hash` input produces the expected public output. There is no algebraic shortcut — the attacker must either find a Poseidon collision (computationally infeasible) or compromise the trusted setup.

---

### Principle 8 — Accountability

**AI Verify test area:** Auditability and traceability of AI system behaviour.

**PTV contribution:**  
Every PTV attestation produces:
1. A **Handshake ID** — deterministic identifier for the agent-device pair
2. A **ZK proof transcript** — cryptographic record of the attestation
3. A **public signals file** — the expected baseline hashes used for verification

These three artefacts together constitute an audit trail that can be verified by any third party holding the verification key — including IMDA, a regulator, or an independent auditor — without the model owner revealing proprietary weights.

**Regulatory relevance:** This directly supports the MAIGF recommendation for *"maintaining logs of AI system decisions and enabling post-hoc review."*

---

### Principle 9 — Human Oversight

**AI Verify test area:** Human-in-the-loop mechanisms and override capability.

**PTV contribution:**  
PTV makes human oversight *actionable*. A human overseer can:
1. Publish the authorised baseline hashes (the "expected" public inputs)
2. Require any agent to produce a valid PTV attestation before its output is accepted
3. Revoke authorisation by changing the expected baseline — all existing proofs immediately become invalid

This gives human overseers a cryptographic enforcement mechanism, not just a policy recommendation.

---

## MAIGF Alignment

| MAIGF Recommendation | PTV Alignment |
|---|---|
| 2.1 — Internal Governance | PTV provides cryptographic enforcement of model governance policies |
| 2.3 — Risk Assessment | Model tamper detection via hash binding |
| 3.1 — Explainability by Design | ZK proof links agent output to specific model version |
| 3.3 — Human Oversight | Verifier role enables revocable authorisation |

---

## What PTV Does Not Address

Honest scoping is important. PTV does **not** address:

| AI Verify Principle | Why PTV Does Not Address It |
|---|---|
| Principle 1 — Fairness | PTV proves model identity, not model fairness. Bias testing requires separate tooling (e.g., AI Verify fairness metrics). |
| Principle 2 — Transparency of data | PTV does not attest to training data provenance — only model weights and policy. |
| Principle 5 — Reproducibility | PTV proves which model ran, not whether it produces consistent outputs. |

PTV is a **trust anchor**, not a comprehensive AI governance solution. It is designed to be composed with complementary tools — AI Verify's fairness and robustness test suites, for example — to form a complete governance stack.

---

## Submission Context

- **OECD.AI Catalogue:** Submitted as a tool addressing AI accountability and transparency
- **IETF Draft:** draft-anandakrishnan-ptv-attested-agent-identity-00 — protocol specification
- **AI Verify Sandbox:** PTV is a candidate for integration testing with IMDA's AI Verify sandbox environment
