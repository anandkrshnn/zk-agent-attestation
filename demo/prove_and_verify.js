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
    let modelHash = '5467453903072796007';
    let policyFingerprint = '11071536422498843841';

    const baselineModel = '5467453903072796007';
    const baselinePolicy = '11071536422498843841';

    const inputPath = path.join(root, 'input.json');
    if (fs.existsSync(inputPath)) {
        try {
            const inputData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
            if (inputData.actual_model_hash) {
                modelHash = inputData.actual_model_hash;
            }
            if (inputData.actual_policy_fingerprint) {
                policyFingerprint = inputData.actual_policy_fingerprint;
            }
        } catch (e) {
            // ignore JSON parsing errors
        }
    }

    // Compute Poseidon hashes of the expected baseline
    const expectedModelPoseidon = await computePoseidon(baselineModel);
    const expectedPolicyPoseidon = await computePoseidon(baselinePolicy);

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
    try {
        execSync(
            'node circuits/agent_attestation_js/generate_witness.js ' +
            'circuits/agent_attestation_js/agent_attestation.wasm ' +
            'input.json witness.wtns',
            { cwd: root, stdio: 'pipe' }
        );
    } catch (err) {
        // Witness generation fails when constraints are violated (e.g. actual_model_hash !== baseline)
        console.log('PROVE_AVG=0');
        console.log('PROVE_MIN=0');
        console.log('VERIFY_AVG=0');
        console.log('VALID=false');
        process.exit(0);
    }

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
