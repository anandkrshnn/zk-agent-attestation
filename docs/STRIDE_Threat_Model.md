# STRIDE Threat Model: zk-agent-attestation (PTV Protocol)

This document outlines the **STRIDE** security analysis for the Prove-Transform-Verify (PTV) protocol and its reference implementation for AI agent identity.

---

| **Threat** | **PTV Mitigation Strategy** | **Implementation Detail** |
| :--- | :--- | :--- |
| **S**poofing | **Hardware-Anchored Identity** | Identity is bound to a TPM 2.0 / Secure Enclave private key that cannot be exported. |
| **T**ampering | **Model & Policy Hashing** | Circuit input signals include SHA-256 hashes of the model weights and orchestration policy. |
| **R**epudiation | **Cryptographic Proofs** | Every agent action is preceded by a ZKP that serves as a non-repudiable proof of state. |
| **I**nformation Disclosure | **Zero-Knowledge Proofs** | Sensitive internal state (hardware raw measurements) is transformed into a ZKP, leaking zero metadata. |
| **D**enial of Service | **Lightweight Verification** | Groth16 verification is extremely fast (~ms), preventing verification-side resource exhaustion. |
| **E**levation of Privilege | **Policy Enforcement** | The ZKP only verifies if the agent's current state matches the authorized baseline policy. |

---

## AI Agent Specific Vectors

### 1. Model Poisoning / Hijacking
- **Threat**: An attacker replaces the model weights or the orchestration script to change agent behavior.
- **Mitigation**: The PTV flow includes a measurement of the model hash (`model_hash`) and the policy fingerprint (`policy_fingerprint`) inside the ZK circuit. Any change to the model or policy will result in a verification failure.

### 2. Side-Channel Extraction
- **Threat**: Extracting identity keys from the agent's memory.
- **Mitigation**: The PTV protocol leverages the **Hardware Root of Trust**. Keys are never exposed to the agent's operating environment; all signing and attestation happen within the secure hardware boundary.

### 3. Orchestration Bypass
- **Threat**: The agent attempts to bypass the PTV check and interact directly with resources.
- **Mitigation**: Relying parties (Orchestrators/Gateways) must require a valid ZKP before granting access or processing agent outputs.

---

**Built for trusted, sovereign, and verifiable AI agents.**
