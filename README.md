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
│TRANSFORM │  Groth16 ZK proof        │  circom + snarkjs │
│          │  generated from witness  │  library mode     │
├──────────┼──────────────────────────┼───────────────────┤
│  VERIFY  │  Verifier checks proof   │  ~9ms verify      │
│          │  against public baseline │  (public key)     │
└──────────┴──────────────────────────┴───────────────────┘
```

---

## 📊 Benchmark Results (10 runs each, Windows 11, Node.js v24, snarkjs v0.7)

| Config | Method | Prove Avg | Prove Min | Verify Avg |
|---|---|---|---|---|
| 1 | Custom circuit, CLI (`--O0`) | 435ms | 420ms | — |
| 2 | circomlib IsEqual, CLI | 435ms | 411ms | — |
| 3 | snarkjs library, no CLI overhead | 45.9ms | 21ms | — |
| **4** | **snarkjs library, prove + verify** | **44.9ms** | **21ms** | **8.8ms** |

> **Key insight:** CLI configs (1 & 2) include ~410ms of Node.js startup overhead unrelated to cryptography. Library mode (configs 3 & 4) reflects real production API performance. Warm proof time is consistently **~24ms**. Total attestation round-trip: **~33ms**.

---

## 🛠️ Quick Start

### Prerequisites
```bash
npm install snarkjs circomlib
# circom binary: https://github.com/iden3/circom/releases (add to PATH)
```

### Run the full pipeline
```bash
# 1. Compile circuit (--O0 preserves all constraints)
circom circuits/agent_attestation.circom --r1cs --wasm --sym -o circuits/ --O0

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

# 5. Prove + Verify (library mode - production performance)
node -e "const snarkjs=require('snarkjs');const fs=require('fs');const vkey=JSON.parse(fs.readFileSync('verification_key.json'));(async()=>{const{proof,publicSignals}=await snarkjs.groth16.prove('circuit_final.zkey','witness.wtns');const ok=await snarkjs.groth16.verify(vkey,publicSignals,proof);console.log('Valid:',ok);process.exit(0);})();"
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

- Hash inputs are field elements (integers); full SHA-256 in-circuit requires Poseidon hash (planned)
- `--O0` disables circom optimiser; production circuits should use circomlib's IsEqual with optimiser enabled
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
