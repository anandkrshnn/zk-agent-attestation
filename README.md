# zk-agent-attestation
**Hardware-anchored identity and verifiable trust for autonomous AI agents.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Groth16](https://img.shields.io/badge/zk--SNARK-Groth16-8A2BE2)](https://github.com/iden3/snarkjs)
[![TPM 2.0](https://img.shields.io/badge/Hardware%20Root-TPM%202.0-orange)](https://trustedcomputinggroup.org/)
[![Status](https://img.shields.io/badge/Status-Active_Development-yellow.svg)](https://github.com/anandkrshnn/zk-agent-attestation)
[![Version](https://img.shields.io/badge/Version-v0.1.0-green.svg)](https://github.com/anandkrshnn/zk-agent-attestation/releases/tag/v0.1.0)

**Hardware-Anchored Zero-Knowledge Attestation for AI Agents**

Part of the **Prove-Transform-Verify (PTV) Protocol** — Reference implementation for trusted, sovereign, and verifiable **AI agent identity**.

---

## Table of Contents
- [Why PTV?](#why-ptv)
- [Architecture](#architecture)
- [Use Cases](#use-cases)
- [Quick Start](#quick-start)
- [Reproducibility & Benchmarks](#reproducibility--benchmarks)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Related Work](#related-work)

---

## Why PTV?

In 2026, autonomous AI agents are moving into production, but **agent identity and trust** remain the biggest bottleneck.

Traditional methods fail for agentic systems because agents act autonomously across clouds and jurisdictions, can be hijacked, and must prove compliance in regulated environments.

**PTV (Prove → Transform → Verify)** solves this by providing:
- Hardware-anchored identity using TPM 2.0 / Secure Enclave
- Privacy-preserving proofs via Groth16 zk-SNARKs
- Verifiable compliance without exposing sensitive data or model weights
- Full **STRIDE** threat model coverage

---

## Architecture

```mermaid
graph TD
    A[AI Agent] --> B[TPM 2.0 / Secure Enclave]
    B --> C[Collect Attestation + Claims]
    C --> D["Raw Claims\n(Model Hash, Policy,\nHardware State)"]
    D --> E[Groth16 zk-SNARK Circuit]
    E --> F[Zero-Knowledge Proof (ZKP)]
    F --> G[Verifier / Orchestrator]
    G --> H{Valid?}
    H -->|Yes| I[Grant Trust & Access]
    H -->|No| J[Reject]
```

**Core Flow**: Prove → Transform → Verify

---

## Use Cases

**Healthcare**: Cross-border medical agents proving data residency and consent compliance.  
**Finance**: Autonomous trading/risk agents proving AML/KYC and model integrity.  
**Enterprise Sovereign AI**: Secure multi-cloud agent orchestration with cryptographic trust.

---

## Quick Start

### Prerequisites
- Python 3.10+
- circom + snarkjs (for Groth16)

### Installation

```bash
git clone https://github.com/anandkrshnn/zk-agent-attestation.git
cd zk-agent-attestation

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Run Demo

```bash
python main.py --mode demo
```

---

## Reproducibility & Benchmarks

- **Average Proof Generation Time**: **187ms ± 23ms** (10,000 runs)
- **Hardware**: Tested on Intel i7 + TPM 2.0

To reproduce:

```bash
python run_benchmarks.py --iterations 10000
```

---

## Project Structure

```
zk-agent-attestation/
├── circuits/                 # Groth16 circuits (circom)
├── src/
│   ├── prove.py              # Prove phase logic
│   ├── transform.py          # ZKP generation
│   ├── verify.py             # Verification logic
│   └── utils.py
├── tests/
│   ├── test_ptv_flow.py
│   └── test_benchmarks.py
├── benchmarks/               # Benchmark results and reports
├── docs/
│   ├── STRIDE_Threat_Model.md
│   └── PTV_Protocol_Guide.md
├── main.py
├── run_benchmarks.py
├── requirements.txt
└── README.md
```

---

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License
Apache License 2.0 — see [LICENSE](LICENSE) file.

---

## Related Work
- IETF RATS Draft: Prove-Transform-Verify (PTV) Protocol
- NIST NCCoE Submission (March 30, 2026)
- Sovereign AI Stack: https://github.com/anandkrshnn/sovereign-ai-stack

---

**Made with ❤️ for trusted, sovereign, and verifiable AI agents.**
