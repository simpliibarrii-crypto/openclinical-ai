# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < older | :x:                |

## Reporting a Vulnerability

We take security seriously, especially given the healthcare context. If you discover a vulnerability:

1. **DO NOT** open a public issue.
2. Email security@openclinical-ai.example with details.
3. We will acknowledge within 48 hours and provide a remediation timeline.

For critical vulnerabilities (PHI exposure, model tampering, audit log bypass), we aim to ship a fix within 7 days.

## Scope

In scope:
- Inference runtime vulnerabilities (sandbox escape, model poisoning)
- Audit gateway tampering or bypass
- Consent engine bypass
- Registry signature verification bypass
- FHIR auth/authz bypass
- PHI leakage via inference

Out of scope:
- Issues in upstream dependencies (report to them)
- Hospital infrastructure-level attacks (report to hospital IT)
- Social engineering