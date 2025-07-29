# Security Policy

## Supported Versions

We actively support the following versions of `sphinxcontrib-jsontable`:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in `sphinxcontrib-jsontable`, please report it to us responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Email**: Send a detailed report to `sasakamacode@gmail.com` with the subject line "SECURITY: sphinxcontrib-jsontable vulnerability"
2. **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature (preferred)

### What to Include

When reporting a vulnerability, please include:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact and severity assessment
- Any suggested fixes or mitigations (if available)
- Your contact information for follow-up questions

### Response Timeline

We will respond to security reports as follows:

- **Acknowledgment**: Within 48 hours of receiving the report
- **Initial Assessment**: Within 5 business days
- **Fix Development**: Timeframe depends on complexity and severity
- **Public Disclosure**: After fix is released and users have time to update

### Security Update Process

1. We will investigate and verify the reported vulnerability
2. Develop and test a fix in a private repository
3. Prepare a security advisory with details and mitigation steps
4. Release a patched version
5. Publish the security advisory and notify users

### Disclosure Policy

- We follow responsible disclosure principles
- We will coordinate with the reporter on disclosure timeline
- We will credit the reporter (unless they prefer to remain anonymous)
- Critical vulnerabilities will be disclosed within 90 days of the fix being available

### Security Best Practices for Users

When using `sphinxcontrib-jsontable`:

1. **Keep Updated**: Always use the latest version
2. **Review Dependencies**: Regularly update Sphinx and other dependencies
3. **Input Validation**: Validate JSON input files before processing
4. **File Permissions**: Ensure proper file permissions for JSON data files
5. **Monitor Advisories**: Watch for security advisories

### Dependencies Security

We regularly monitor our dependencies for security vulnerabilities:

- **Automated Scanning**: GitHub Dependabot alerts
- **CI Security Checks**: `safety` tool in our CI pipeline
- **Regular Updates**: We update dependencies to address security issues

### Contact

For any security-related questions or concerns:
- Email: `sasakamacode@gmail.com`
- GitHub: [@sasakama-code](https://github.com/sasakama-code)

---

Thank you for helping keep `sphinxcontrib-jsontable` and our community safe!
