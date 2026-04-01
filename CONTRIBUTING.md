# Contributing to zk-agent-attestation

First off, thank you for considering contributing to the **Prove-Transform-Verify (PTV) Protocol** reference implementation! It's people like you that make this ecosystem robust.

---

## 🚀 How to Contribute

1.  **Fork the Repository**: Create your own copy of the project.
2.  **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3.  **Commit Your Changes**: `git commit -m 'Add some amazing feature'`
4.  **Push to the Branch**: `git push origin feature/amazing-feature`
5.  **Open a Pull Request**: Submit your changes for review.

---

## 📋 Guidelines

-   **Code Style**: Follow PEP 8 for Python code and ensure `circom` circuits are well-commented.
-   **Tests**: Ensure all tests in the `tests/` directory pass before submitting a PR.
-   **Security**: Since this is a security-critical project (ZKP + TPM), avoid introducing dependencies without a clear security audit.
-   **ZKP Reproducibility**: When modifying circuits, provide a summary of the `snarkjs` benchmarks (proof generation time, constraint count).

---

## ⚖️ License

By contributing, you agree that your contributions will be licensed under its **Apache License 2.0**.

---

**Made with ❤️ for trusted, sovereign, and verifiable AI agents.**
