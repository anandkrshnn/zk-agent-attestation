const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const snarkjs = require('snarkjs');
const { buildPoseidon } = require('circomlibjs');

const root = path.join(__dirname, '..');

async function getPoseidonHash(chunks) {
    const poseidon = await buildPoseidon();
    const hash = poseidon(chunks.map(c => BigInt(c)));
    return poseidon.F.toString(hash);
}

// Splits a 64-char hex string into two 128-bit integers as decimal strings
function splitSha256ToChunks(hex) {
    if (hex.length !== 64) {
        throw new Error("Invalid hex string length for SHA-256");
    }
    const chunk0 = BigInt("0x" + hex.slice(0, 32)).toString();
    const chunk1 = BigInt("0x" + hex.slice(32, 64)).toString();
    return [chunk0, chunk1];
}

async function run() {
    console.log("=== Multi-Field Circuit Verification & Trusted Setup ===");

    const modelHashHex = "a8f5e1329c0f456ba178d24b6e5111002233445566778899aabbccddeeff0011";
    const policyHashHex = "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00";

    const modelChunks = splitSha256ToChunks(modelHashHex);
    const policyChunks = splitSha256ToChunks(policyHashHex);

    console.log("Model chunks (128-bit):", modelChunks);
    console.log("Policy chunks (128-bit):", policyChunks);

    const modelPoseidon = await getPoseidonHash(modelChunks);
    const policyPoseidon = await getPoseidonHash(policyChunks);

    console.log("Poseidon(Model chunks):", modelPoseidon);
    console.log("Poseidon(Policy chunks):", policyPoseidon);

    const inputData = {
        actual_model_hash_chunks: modelChunks,
        actual_policy_fingerprint_chunks: policyChunks,
        expected_model_hash_poseidon: modelPoseidon,
        expected_policy_poseidon: policyPoseidon
    };

    fs.writeFileSync(path.join(root, 'input_multi.json'), JSON.stringify(inputData, null, 2));
    console.log("Saved input_multi.json");

    // 1. Compile the multi-field circuit using circom.exe
    console.log("\n[1/4] Compiling poseidon_multi.circom...");
    const circomPath = "C:\\circom\\circom.exe";
    execSync(
        `"${circomPath}" circuits/poseidon_multi.circom --r1cs --wasm --sym --output circuits/`,
        { stdio: 'inherit', cwd: root }
    );
    console.log("Compilation complete.");

    // 2. Perform Groth16 Setup
    console.log("\n[2/4] Executing Groth16 trusted setup...");
    execSync(
        "npx snarkjs groth16 setup circuits/poseidon_multi.r1cs pot12_final.ptau circuits/poseidon_multi_0000.zkey",
        { stdio: 'inherit', cwd: root }
    );
    // Contribute
    execSync(
        "npx snarkjs zkey contribute circuits/poseidon_multi_0000.zkey circuits/poseidon_multi_final.zkey --name=\"1st Contributor\" -v -e=\"random entropy text\"",
        { stdio: 'inherit', cwd: root }
    );
    // Export verification key
    execSync(
        "npx snarkjs zkey export verificationkey circuits/poseidon_multi_final.zkey circuits/poseidon_multi_verification_key.json",
        { stdio: 'inherit', cwd: root }
    );
    console.log("Setup complete. Verification key exported.");

    // 3. Generate Witness
    console.log("\n[3/4] Generating witness...");
    execSync(
        "node circuits/poseidon_multi_js/generate_witness.js circuits/poseidon_multi_js/poseidon_multi.wasm input_multi.json circuits/witness_multi.wtns",
        { stdio: 'inherit', cwd: root }
    );
    console.log("Witness generated successfully.");

    // 4. Prove & Verify
    console.log("\n[4/4] Generating and verifying proof...");
    const vkey = JSON.parse(fs.readFileSync(path.join(root, 'circuits/poseidon_multi_verification_key.json')));

    const { proof, publicSignals } = await snarkjs.groth16.prove(
        path.join(root, 'circuits/poseidon_multi_final.zkey'),
        path.join(root, 'circuits/witness_multi.wtns')
    );
    console.log("ZK proof generated.");
    
    fs.writeFileSync(
        path.join(root, 'circuits/poseidon_multi_proof_sample.json'),
        JSON.stringify({ proof, publicSignals }, null, 2)
    );
    console.log("Saved circuits/poseidon_multi_proof_sample.json");

    const ok = await snarkjs.groth16.verify(vkey, publicSignals, proof);
    if (ok) {
        console.log("✅ Proof verification SUCCESSFUL!");
    } else {
        console.error("❌ Proof verification FAILED!");
        process.exit(1);
    }

    // Try verifying with tampered expected public signals
    const tamperedSignals = [...publicSignals];
    tamperedSignals[0] = "999999999999999999999999999"; // Alter model hash signal
    const badVerify = await snarkjs.groth16.verify(vkey, tamperedSignals, proof);
    if (!badVerify) {
        console.log("✅ Tampered public signal correctly rejected.");
    } else {
        console.error("❌ Mismatch verification check FAILED (accepted bad signals)!");
        process.exit(1);
    }

    console.log("\n=== All Multi-Field Checks Passed Successfully ===");
    process.exit(0);
}

run().catch(err => {
    console.error(err);
    process.exit(1);
});
