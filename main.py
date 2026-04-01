#!/usr/bin/env python3
"""
zk-agent-attestation — CLI Entry Point (v1.0)
The unified interface for the PTV protocol on the Sovereign Edge.
"""

import argparse
import sys
import os
from src.utils import log, save_json, load_json
from src.prove import collect_claims, generate_proof
from src.verify import verify_proof

def run_demo():
    """Execute a full Prove-Transform-Verify flow demonstration"""
    log("🚀 Starting PTV Proof-of-Trust Demonstration...")
    
    # 1. Prove: Collect claims for a medical AI model
    model = "Sovereign-Llama-3-8B"
    policy = "config/policy_ICU_v1.yaml"
    claims = collect_claims(model, policy)
    
    # 2. Transform: Generate ZKP
    proof = generate_proof(claims)
    
    # 3. Verify: Proof verification
    expected_signals = [claims["model_hash"], claims["policy_fingerprint"]]
    is_valid = verify_proof(proof, expected_signals)
    
    if is_valid:
        log("🏆 PTV Demonstration Successful! Agent identity is secure and verifiable.")
    else:
        log("❌ PTV Demonstration Failed!")

def main():
    parser = argparse.ArgumentParser(description="zk-agent-attestation — PTV Protocol CLI")
    parser.add_argument("--mode", choices=["prove", "verify", "demo"], default="demo", help="Execution mode")
    parser.add_argument("--model", type=str, default="DefaultAI", help="Model name for attestation")
    parser.add_argument("--policy", type=str, default="default_policy.yaml", help="Path to policy file")
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        run_demo()
    elif args.mode == "prove":
        claims = collect_claims(args.model, args.policy)
        proof = generate_proof(claims)
        save_json(proof, "proof.json")
        log("Proof saved to: proof.json")
    elif args.mode == "verify":
        if os.path.exists("proof.json"):
            proof = load_json("proof.json")
            # In a real verify, you would also pass the expected public signals
            verify_proof(proof, proof.get("public_signals", []))
        else:
            log("❌ No proof.json found. Run in 'prove' mode first.")

if __name__ == "__main__":
    main()
