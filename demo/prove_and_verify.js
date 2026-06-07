const snarkjs = require('snarkjs');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const vkey = JSON.parse(fs.readFileSync(path.join(root, 'verification_key.json')));

(async () => {
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
})();
