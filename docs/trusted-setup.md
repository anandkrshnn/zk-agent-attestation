# Trusted Setup — PTV Protocol Ceremony Documentation

## Overview

The PTV protocol uses a **Groth16 zk-SNARK**, which requires a one-time trusted setup ceremony to generate the proving key (`circuit_final.zkey`) and verification key (`verification_key.json`). This document explains what the current setup means, what its limitations are, and what a production-grade ceremony requires.

---

## What the Current Setup Does

The current trusted setup was performed locally using snarkjs with the following steps:

```bash
snarkjs powersoftau new bn128 12 pot12_0000.ptau
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="contributor" -e="random entropy"
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau
snarkjs groth16 setup circuits/agent_attestation.r1cs pot12_final.ptau circuit_0000.zkey
snarkjs zkey contribute circuit_0000.zkey circuit_final.zkey --name="ptv-v1" -e="random entropy"
```

The phrase `"random entropy"` is a string passed to snarkjs as the randomness source for the ceremony contribution. In this prototype, it is a static placeholder.

---

## Why This Is Acceptable for a Research Prototype

A Groth16 trusted setup is "toxic waste" — if the randomness used during the ceremony is known, a malicious prover could generate false proofs. However:

1. **This repository is a reference implementation**, not a production deployment. No real assets, identities, or decisions are protected by this proof.
2. **The verifier key is public** — any party can independently verify proofs using `verification_key.json`.
3. **The circuit logic is correct regardless of the setup** — the 426-constraint Poseidon circuit enforces the correct relationship between inputs and outputs. A compromised setup affects proof forgery, not proof verification correctness.
4. **Prototype scope** — the PTV protocol is proposed as a reference design in alignment with OECD.AI and IETF drafts. The trusted setup ceremony is explicitly flagged as requiring a production upgrade before any real-world deployment.

---

## What a Production Ceremony Requires

A production-grade Groth16 trusted setup must follow the **Powers of Tau multi-party computation (MPC)** model:

| Requirement | Current Status | Production Requirement |
|---|---|---|
| Number of contributors | 1 (single party) | ≥ 6 independent parties |
| Entropy source | Static string | Hardware RNG / atmospheric noise |
| Contributor verification | None | Identity-attested participants |
| Transcript published | No | Yes — publicly auditable |
| Ceremony tool | snarkjs local | Hermez/Semaphore ceremony infrastructure |
| Toxic waste destruction | Not applicable | Verified deletion by each contributor |

**Security guarantee:** A multi-party ceremony is secure as long as **at least one contributor** honestly discards their randomness. This is why independent, geographically distributed contributors are critical.

---

## Reference Ceremonies

- **Zcash Sapling (2018)** — 87 independent contributors across 6 continents. Transcript publicly available.
- **Hermez Network (2021)** — 214 contributions. First ceremony to use a web-based contribution tool.
- **Semaphore (2022)** — Open public ceremony, >1000 contributors.

The PTV v2 production ceremony will follow the Semaphore model — open public participation with a published transcript hosted on IPFS.

---

## Powers of Tau Parameter Choice

The current setup uses `bn128 12` — meaning the Powers of Tau supports up to 2^12 = **4096 constraints**. The current circuit has 426 constraints, leaving ample headroom for v2 and v3 circuit expansions (multi-field hashing, PCR binding) without requiring a new ceremony.

---

## v2 Ceremony Plan

1. Coordinate ≥ 6 independent contributors from cryptography community
2. Use hardware RNG entropy (TPM-sourced randomness preferred)
3. Publish ceremony transcript to IPFS
4. Reference transcript hash in IETF draft appendix
5. Update `circuit_final.zkey` and `verification_key.json` with ceremony output
