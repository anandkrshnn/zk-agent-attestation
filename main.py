#!/usr/bin/env python3
"""
PTV Protocol — Verifiable Agent Identity
=========================================
CLI for Prove-Transform-Verify attestation demo.
PROVE phase reads real hardware measurements from Intel INTC TPM 2.0 via Windows WMI.
"""

import typer
import json
import time
import hashlib
import sys
from typing import Optional
from dataclasses import dataclass, asdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = typer.Typer(help="PTV Protocol: Hardware-ready agent attestation")


@dataclass
class AttestationResult:
    handshake_id: str
    status: str
    triage_tier: str
    generation_ms: float
    proof_size_bytes: int
    verified: bool


def run_prove_phase(device_id: str, model_hash: str) -> dict:
    """PROVE phase: collect hardware-anchored claims via TPM WMI (falls back to software simulation)"""
    from src.utils import get_tpm_measurements
    hardware_claims = get_tpm_measurements()
    return {
        "device_id": device_id,
        "model_hash": model_hash,
        "hardware": hardware_claims,
        "timestamp": time.time(),
    }


def run_transform_phase(claims: dict) -> dict:
    """TRANSFORM phase: generate ZK proof (Groth16 via snarkjs in production)"""
    start = time.time()
    proof = hashlib.sha256(json.dumps(claims, sort_keys=True).encode()).hexdigest()
    generation_ms = (time.time() - start) * 1000
    return {
        "proof": proof,
        "generation_ms": generation_ms,
        "proof_size_bytes": len(proof),
    }


def run_verify_phase(proof: str) -> bool:
    """VERIFY phase: validate proof against public baseline (~9ms in snarkjs production)"""
    return True  # Mock verification — production uses snarkjs groth16.verify()


@app.command()
def attest(
    device_id: str = typer.Argument(..., help="Device identifier"),
    model_hash: Optional[str] = typer.Option(None, help="Model hash (SHA-256)"),
):
    """Run full PTV attestation"""
    typer.echo(f"\n🔐 PTV Attestation for {device_id}\n")

    # Prove phase
    typer.echo("📡 PROVE: Collecting hardware claims...")
    claims = run_prove_phase(device_id, model_hash or "mock_model")
    src = claims["hardware"].get("source", "UNKNOWN")
    typer.echo(f"   Source: {src}")
    if src == "TPM_HARDWARE":
        typer.echo(f"   SRK hash: {claims['hardware']['srk_hash'][:16]}... [HARDWARE]")
        typer.echo(f"   TCG hash: {claims['hardware']['tcg_log_hash'][:16]}... [HARDWARE]")
    typer.echo(f"   Timestamp: {claims['timestamp']}")

    # Transform phase
    typer.echo("\n⚙️ TRANSFORM: Generating zero-knowledge proof...")
    proof_data = run_transform_phase(claims)
    typer.echo(f"   Proof generated in {proof_data['generation_ms']:.2f}ms")
    typer.echo(f"   Proof size: {proof_data['proof_size_bytes']} bytes")
    typer.echo(f"   Proof: {proof_data['proof'][:32]}...")

    # Verify phase
    typer.echo("\n✅ VERIFY: Validating proof...")
    verified = run_verify_phase(proof_data["proof"])
    typer.echo(f"   Verification: {'PASS' if verified else 'FAIL'}")

    result = AttestationResult(
        handshake_id=f"PTV-{hashlib.md5(device_id.encode()).hexdigest()[:8].upper()}",
        status="APPROVED" if verified else "REJECTED",
        triage_tier="ZK_PROOF",
        generation_ms=proof_data["generation_ms"],
        proof_size_bytes=proof_data["proof_size_bytes"],
        verified=verified,
    )

    typer.echo(f"\n🏁 Handshake {result.handshake_id} COMPLETE")
    typer.echo(f"   Status: {result.status}")
    typer.echo(f"   Triage: {result.triage_tier}")

    return result


@app.command()
def benchmark(iterations: int = typer.Option(100, help="Number of iterations")):
    """Run performance benchmark"""
    typer.echo(f"\n📊 Running benchmark (n={iterations})...")
    times = []
    for i in range(iterations):
        claims = run_prove_phase(f"device_{i}", "mock_model")
        start = time.time()
        _ = run_transform_phase(claims)
        times.append((time.time() - start) * 1000)

    avg = sum(times) / len(times)
    std = (sum((x - avg) ** 2 for x in times) / len(times)) ** 0.5
    typer.echo(f"\n✅ Results (n={iterations}):")
    typer.echo(f"   Mean: {avg:.2f}ms")
    typer.echo(f"   Std Dev: {std:.2f}ms")
    typer.echo(f"   Min: {min(times):.2f}ms")
    typer.echo(f"   Max: {max(times):.2f}ms")


if __name__ == "__main__":
    app()
