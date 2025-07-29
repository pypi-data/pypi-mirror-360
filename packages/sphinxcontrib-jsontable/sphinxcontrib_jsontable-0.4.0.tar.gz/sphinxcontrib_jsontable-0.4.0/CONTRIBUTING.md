# Contributing to sphinxcontrib-jsontable

Thank you for your interest in contributing to **sphinxcontrib-jsontable**! We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code enhancements.

## How to File an Issue

1. Check the [issue tracker](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues) to see if your issue has already been reported.
2. If not, open a new issue and include:

   * A clear and descriptive title.
   * A detailed description of the problem or feature request.
   * Steps to reproduce, if applicable.
   * Versions of Python, Sphinx, and `sphinxcontrib-jsontable` you are using.
   * Sample code or JSON input that triggers the issue.

## Forking and Branching

1. Fork the repository on GitHub.
2. Clone your fork locally:

   ```bash
   git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
   cd sphinxcontrib-jsontable
   ```
3. Create a feature branch:

   ```bash
   git checkout -b feature/awesome-feature
   ```

## Code Style and Testing

* **Code style**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) standards.
* **Imports**: Group imports in the order: standard library, third-party, local packages.
* **Testing**: Add or update tests in the `tests/` directory. Verify they pass:

  ```bash
  pytest
  ```
* **Type hints**: Use type annotations consistent with existing code.

## Submitting a Pull Request

1. Ensure your branch is up to date with the main repository:

   ```bash
   git fetch upstream
   git merge upstream/main
   ```
2. Commit your changes with clear, descriptive messages.
3. Push to your fork:

   ```bash
   git push origin feature/awesome-feature
   ```
4. Open a PR against the `main` branch of the upstream repository.
5. Describe your changes, referencing any relevant issues.

## Continuous Integration

* We use GitHub Actions for CI (see `.github/workflows/ci.yml`).
* Ensure your changes pass all checks before requesting review.

## License and Code of Conduct

By contributing, you agree that your contributions will be licensed under the project’s MIT License.

Please also read and abide by our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.
