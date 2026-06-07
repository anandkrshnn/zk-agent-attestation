# PTV Demo — IMDA Briefing Script

## Prerequisites

1. Node.js installed
2. circom binary at `C:\circom\circom.exe`
3. Trusted setup complete (`circuit_final.zkey`, `verification_key.json` in root)
4. Run from repo root: `npm install`

## Run the demo

```powershell
cd C:\Users\Monika\Documents\GitHub\zk-agent-attestation
powershell -ExecutionPolicy Bypass -File demo\run_demo.ps1
```

## What it shows

1. The circuit (what is being proved)
2. Agent identity inputs (model hash + policy fingerprint)
3. ZK witness generation
4. Groth16 proof generation with timing (5 warm runs)
5. Results: prove time, verify time, proof validity

## Expected output

```
Proof generation (avg): ~24 ms
Verification time (avg): ~9 ms
Proof valid: true
Total round-trip: ~33ms (warm)
Private inputs: NEVER REVEALED
```

## For the IMDA briefing

- Run this script live during the demo portion
- The `NEVER REVEALED` line is the key message: verifier learns nothing about the model except that it matches the baseline
- All timings are measured live on the machine, not hardcoded
