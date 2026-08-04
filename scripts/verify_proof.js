const snarkjs = require('snarkjs');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');

async function main() {
    try {
        const inputPath = process.argv[2];
        if (!inputPath) {
            console.error("Missing input file path argument");
            process.exit(2);
        }

        const data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
        const { proof, publicSignals } = data;

        if (!proof || !publicSignals) {
            console.error("Missing proof or publicSignals in input JSON");
            process.exit(3);
        }

        // Load the multi-field verification key
        const vkeyPath = path.join(root, 'circuits/poseidon_multi_verification_key.json');
        if (!fs.existsSync(vkeyPath)) {
            console.error("Verification key not found at:", vkeyPath);
            process.exit(4);
        }
        
        const vkey = JSON.parse(fs.readFileSync(vkeyPath, 'utf8'));
        const ok = await snarkjs.groth16.verify(vkey, publicSignals, proof);
        
        if (ok) {
            console.log("SUCCESS");
            process.exit(0);
        } else {
            console.log("FAIL");
            process.exit(1);
        }
    } catch (err) {
        console.error("Error during verification:", err.message);
        process.exit(5);
    }
}

main();
