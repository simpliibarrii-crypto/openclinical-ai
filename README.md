# OpenClinical AI

[![License](https://img.shields.io/github/license/simpliibarrii-crypto/openclinical-ai?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/simpliibarrii-crypto/openclinical-ai/ci-python.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/simpliibarrii-crypto/openclinical-ai/actions)
[![Raven Clinical](https://img.shields.io/badge/Raven-Clinical_Layer-C8102E?style=for-the-badge&labelColor=05060A)](https://github.com/simpliibarrii-crypto/raven-ai)

**OpenClinical AI is the healthcare deployment layer inside the Raven AI ecosystem.**

It focuses on local-first clinical AI infrastructure: tenant-aware runtime, consent, audit logs, model governance, evidence retrieval, and safe deployment patterns for healthcare and home-care workflows.

## Role in the Raven ecosystem

- **Raven AI** is the flagship biology and healthcare agent platform.
- **OpenClinical AI** is the bounded clinical deployment layer.
- **Home for AI** is the local orchestration environment.

## Current focus

- PHI-aware workflow support.
- Auditability and tenant isolation.
- Clinical evidence retrieval and governance.
- Affordable inference and edge-friendly deployment.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest pynacl
pytest -q
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Security

Report security issues privately. See [SECURITY.md](SECURITY.md).
