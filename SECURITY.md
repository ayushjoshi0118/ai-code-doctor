# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

The AI Code Doctor maintainers take security seriously. If you discover a vulnerability or security flaw, please do **NOT** open a public issue.

Instead, please send an email to the repository owner or submit a private security advisory on GitHub.

Please include:
- A description of the issue and potential impact
- Steps or proof-of-concept to reproduce the vulnerability
- Any proposed remediation or patches

We will acknowledge receipt within 48 hours and work with you to release a coordinated security patch.

## Secret Handling & Sandboxing Note

- AI Code Doctor does not store or transmit your API keys to any third-party telemetry services. All calls go directly to the Google Gemini API.
- Code executed via the Pytest Sandbox runs locally on the host machine. Ensure you do not run untrusted code containing dangerous system calls or filesystem mutations.
