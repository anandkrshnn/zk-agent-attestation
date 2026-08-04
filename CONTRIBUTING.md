# Contributing to zk-agent-attestation

Thank you for considering contributing to this project!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure tests pass (`pytest`)
5. Commit your changes with a DCO sign-off (see below)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Developer Certificate of Origin (DCO)

To ensure clear chain of custody for open source contributions, we require all commits to be signed off using the Developer Certificate of Origin (DCO). By signing off, you certify that you have the right to submit the code under the Apache 2.0 license.

To sign off, add a `-s` flag to your git commit command:
```bash
git commit -s -m "Add amazing feature"
```
This appends a line to your commit message:
`Signed-off-by: Your Name <your.email@example.com>`

---

## Contributor License Agreement (CLA)

By contributing to this repository, you agree that your contributions will be licensed under the project's Apache License 2.0. If you are representing a corporation or plan to submit work that will be proposed to standards bodies (e.g., IETF), you warrant that you have the authority to contribute such work.

---

## Third-Party Cryptographic Dependencies

The ZK proof pipeline in this project relies on:
- [iden3/circom](https://github.com/iden3/circom) (GPL-3.0)
- [SnarkJS](https://github.com/iden3/snarkjs) (GPL-3.0)
- [circomlib](https://github.com/iden3/circomlib) (MIT / GPL-3.0)

Please ensure any additions or changes to circuit logic or cryptographic helper utilities respect the licensing of these dependencies and do not introduce licensing conflicts.

---

## Reporting Issues

Please use the GitHub Issues tab with a clear title and description, including:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)

## Code Style

- Follow PEP 8 guidelines for Python code
- Write meaningful commit messages
- Add tests for new functionality
