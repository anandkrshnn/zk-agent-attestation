# zk-agent-attestation

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Groth16](https://img.shields.io/badge/zk--SNARK-Groth16-8A2BE2)](https://github.com/iden3/snarkjs)
[![TPM 2.0](https://img.shields.io/badge/Hardware%20Root-TPM%202.0-orange)](https://trustedcomputinggroup.org/)
[![Benchmark](https://img.shields.io/badge/Benchmark-187ms-success)](benchmarks/)

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

In 2026, autonomous AI agents are moving into production, but **agent identity and trust** remain the biggest challenge.

Traditional methods fail because agents act autonomously across clouds and jurisdictions, can be hijacked, and must prove compliance in regulated environments.

The **Prove-Transform-Verify (PTV)** protocol addresses this challenge by delivering:
- **Hardware-anchored identity** (TPM 2.0 / Secure Enclave)
- **Privacy-preserving proofs** using Groth16 zk-SNARKs
- **Verifiable compliance** without leaking sensitive data
- Full coverage of the **STRIDE** threat model

---

## Architecture

```mermaid
graph TD
    A[AI Agent] --> B[TPM 2.0 / Secure Enclave]
    B --> C[Collect Attestation + Claims]
    C --> D[Raw Claims<br>(Model Hash, Policy, Hardware State)]
    D --> E[Groth16 zk-SNARK Circuit]
    E --> F[Zero-Knowledge Proof (ZKP)]
    F --> G[Verifier / Orchestrator]
    G --> H{Valid?}
    H -->|Yes| I[Grant Trust & Access]
    H -->|No| J[Reject]
```

**Core Flow (Prove → Transform → Verify)**:
1. **Prove** — Agent generates hardware-backed cryptographic claims
2. **Transform** — Convert claims into a compact, privacy-preserving Groth16 ZKP
3. **Verify** — Fast and lightweight verification by the relying party

---

## Use Cases

### Healthcare
- Cross-border medical AI agents proving compliance with data residency and consent rules without exposing patient records
- Verifiable multi-agent diagnostic and treatment planning workflows

### Finance
- Autonomous trading and risk agents that cryptographically prove regulatory compliance (AML/KYC), model integrity, and execution policy
- Secure fraud detection agents operating across sovereign cloud boundaries

### Enterprise Sovereign AI
- Multi-cloud and federated agent orchestration with strong trust guarantees
- Compliance-ready agent identity for EU AI Act, NIST guidelines, and similar frameworks

---

## Quick Start

### Prerequisites
- Python 3.10+
- Rust (optional, for circuit compilation)
- circom + snarkjs (for Groth16)

### Installation

```bash
git clone https://github.com/anandkrshnn/zk-agent-attestation.git
cd zk-agent-attestation

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Run Demo

```bash
# Run a basic Prove-Transform-Verify demonstration
python main.py --mode demo
```

---

## Reproducibility & Benchmarks

**Reproducible Benchmark Results**:
- **Average Proof Generation Time**: **187ms ± 23ms**
- **Iterations**: 10,000
- **Test Hardware**: Intel i7 with TPM 2.0

To reproduce the benchmarks:

```bash
python run_benchmarks.py \
  --iterations 10000 \
  --output benchmarks/report.json
```

Full reports, raw data, and statistical analysis are available in the [`benchmarks/`](benchmarks/) directory.

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
│   └── PTV_Whitepaper.pdf
├── main.py
├── run_benchmarks.py
├── requirements.txt
└── README.md
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

---

## Related Work

- **IETF RATS Draft**: [Prove-Transform-Verify (PTV) Protocol for Attested Agent Identity](https://datatracker.ietf.org/doc/draft-anandakrishnan-ptv-attested-agent-identity/)
- **NIST NCCoE Submission** (March 30, 2026): Technical feedback on "Accelerating the Adoption of Software and AI Agent Identity and Authorization"
- **Sovereign AI Stack** (Main Repository): [https://github.com/anandkrshnn/sovereign-ai-stack](https://github.com/anandkrshnn/sovereign-ai-stack)

---

**Built for trusted, sovereign, and verifiable AI agents.**
