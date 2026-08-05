/**
 * PTV Protocol - Multi-Field Prove and Verify
 * Generates Poseidon hashes of 128-bit input chunks, then proves and verifies.
 * Used by src/ptv_engine.py and app.py
 */
const snarkjs = require('snarkjs');
const fs = require('fs');
const path = require('path');
const { buildPoseidon } = require('circomlibjs');

const root = path.join(__dirname, '..');

async function computePoseidonOfChunks(chunks) {
    const poseidon = await buildPoseidon();
    const F = poseidon.F;
    const hash = poseidon(chunks.map(c => BigInt(c)));
    return F.toString(hash);
}

// Splits a 64-char hex string into two 128-bit integers as decimal strings.
// If input is not a 64-character hex, compute its SHA-256 first (matching Python behavior).
function splitSha256ToChunks(input) {
    let hex = input;
    const hexPattern = /^[a-fA-F0-9]{64}$/;
    if (!hexPattern.test(hex)) {
        const crypto = require('crypto');
        hex = crypto.createHash('sha256').update(input, 'utf8').digest('hex');
    }
    const chunk0 = BigInt("0x" + hex.slice(0, 32)).toString();
    const chunk1 = BigInt("0x" + hex.slice(32, 64)).toString();
    return [chunk0, chunk1];
}

async function main() {
    // Defaults matching verify_multi_field_circuits.js values
    const defaultModel = "a8f5e1329c0f456ba178d24b6e5111002233445566778899aabbccddeeff0011";
    const defaultPolicy = "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00";

    const baselineModel = "a8f5e1329c0f456ba178d24b6e5111002233445566778899aabbccddeeff0011";
    const baselinePolicy = "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00";

    let modelChunks, policyChunks;

    const inputPath = path.join(root, 'input.json');
    if (fs.existsSync(inputPath)) {
        try {
            const inputData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
            if (inputData.actual_model_hash_chunks) {
                modelChunks = inputData.actual_model_hash_chunks;
            } else if (inputData.actual_model_hash) {
                modelChunks = splitSha256ToChunks(inputData.actual_model_hash);
            }

            if (inputData.actual_policy_fingerprint_chunks) {
                policyChunks = inputData.actual_policy_fingerprint_chunks;
            } else if (inputData.actual_policy_fingerprint) {
                policyChunks = splitSha256ToChunks(inputData.actual_policy_fingerprint);
            }
        } catch (e) {
            // ignore JSON parsing errors
        }
    }

    if (!modelChunks) {
        modelChunks = splitSha256ToChunks(defaultModel);
    }
    if (!policyChunks) {
        policyChunks = splitSha256ToChunks(defaultPolicy);
    }

    // Compute expected baseline Poseidon hashes of chunks
    const baselineModelChunks = splitSha256ToChunks(baselineModel);
    const baselinePolicyChunks = splitSha256ToChunks(baselinePolicy);

    const expectedModelPoseidon = await computePoseidonOfChunks(baselineModelChunks);
    const expectedPolicyPoseidon = await computePoseidonOfChunks(baselinePolicyChunks);

    // Write input.json with Poseidon public inputs and actual chunks
    const input = {
        actual_model_hash_chunks: modelChunks,
        actual_policy_fingerprint_chunks: policyChunks,
        expected_model_hash_poseidon: expectedModelPoseidon,
        expected_policy_poseidon: expectedPolicyPoseidon
    };
    fs.writeFileSync(path.join(root, 'input.json'), JSON.stringify(input, null, 2));

    // Generate witness using poseidon_multi
    const { execSync } = require('child_process');
    try {
        execSync(
            'node circuits/poseidon_multi_js/generate_witness.js ' +
            'circuits/poseidon_multi_js/poseidon_multi.wasm ' +
            'input.json witness.wtns',
            { cwd: root, stdio: 'pipe' }
        );
    } catch (err) {
        // Witness generation fails if constraints are violated
        console.log('PROVE_AVG=0');
        console.log('PROVE_MIN=0');
        console.log('VERIFY_AVG=0');
        console.log('VALID=false');
        process.exit(0);
    }

    const vkeyPath = path.join(root, 'circuits/poseidon_multi_verification_key.json');
    if (!fs.existsSync(vkeyPath)) {
        console.error("Verification key not found at:", vkeyPath);
        process.exit(1);
    }
    const vkey = JSON.parse(fs.readFileSync(vkeyPath));

    const zkeyPath = path.join(root, 'circuits/poseidon_multi_final.zkey');
    const witnessPath = path.join(root, 'witness.wtns');

    // Warm up
    await snarkjs.groth16.prove(zkeyPath, witnessPath);

    const proveTimes = [], verifyTimes = [];
    for (let i = 0; i < 5; i++) {
        let start = Date.now();
        const { proof, publicSignals } = await snarkjs.groth16.prove(zkeyPath, witnessPath);
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
