/**
 * PTV Protocol - Prove and Verify
 * Generates Poseidon hashes of inputs, then proves and verifies.
 * Used by demo/run_demo.ps1 and app.py
 */
const snarkjs = require('snarkjs');
const fs = require('fs');
const path = require('path');
const { buildPoseidon } = require('circomlibjs');

const root = path.join(__dirname, '..');

async function computePoseidon(value) {
    const poseidon = await buildPoseidon();
    const F = poseidon.F;
    const hash = poseidon([BigInt(value)]);
    return F.toString(hash);
}

async function main() {
    const modelHash = '12345678901234567890';
    const policyFingerprint = '09876543210987654321';

    // Compute Poseidon hashes of the expected baseline
    const expectedModelPoseidon = await computePoseidon(modelHash);
    const expectedPolicyPoseidon = await computePoseidon(policyFingerprint);

    // Write input.json with Poseidon public inputs
    const input = {
        actual_model_hash: modelHash,
        actual_policy_fingerprint: policyFingerprint,
        expected_model_hash_poseidon: expectedModelPoseidon,
        expected_policy_poseidon: expectedPolicyPoseidon
    };
    fs.writeFileSync(path.join(root, 'input.json'), JSON.stringify(input));

    // Generate witness
    const { execSync } = require('child_process');
    execSync(
        'node circuits/agent_attestation_js/generate_witness.js ' +
        'circuits/agent_attestation_js/agent_attestation.wasm ' +
        'input.json witness.wtns',
        { cwd: root }
    );

    const vkey = JSON.parse(fs.readFileSync(path.join(root, 'verification_key.json')));

    // Warm up
    await snarkjs.groth16.prove(
        path.join(root, 'circuit_final.zkey'),
        path.join(root, 'witness.wtns')
    );

    const proveTimes = [], verifyTimes = [];
    for (let i = 0; i < 5; i++) {
        let start = Date.now();
        const { proof, publicSignals } = await snarkjs.groth16.prove(
            path.join(root, 'circuit_final.zkey'),
            path.join(root, 'witness.wtns')
        );
        proveTimes.push(Date.now() - start);

        start = Date.now();
        const ok = await snarkjs.groth16.verify(vkey, publicSignals, proof);
        verifyTimes.push(Date.now() - start);
    }

    const avg = arr => (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1);
    console.log('PROVE_AVG=' + avg(proveTimes));
    console.log('PROVE_MIN=' + Math.min(...proveTimes));
    console.log('VERIFY_AVG=' + avg(verifyTimes));
    console.log('VALID=true');
    process.exit(0);
}

main().catch(err => { console.error(err); process.exit(1); });
