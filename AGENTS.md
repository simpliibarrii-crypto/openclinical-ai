# OpenClinical AI — Agent Context

## Project Overview

OpenClinical AI is a sovereign Canadian-built clinical AI deployment substrate for healthcare systems. It provides local-first clinical AI infrastructure with tenant-aware runtime, patient consent propagation, audit trails, model governance, evidence retrieval, and safe deployment patterns.

## Stack

- **Runtime:** FastAPI + uvicorn (Python 3.11+)
- **Auth:** Multi-tenant API keys, session tokens, OIDC-ready
- **Database:** SQLModel + SQLite (MVP), PostgreSQL-ready
- **FHIR:** fhirclient, SMART-on-FHIR auth patterns
- **Models:** Signed model registry with Ed25519 verification
- **Audit:** Per-tenant append-only audit logging
- **Consent:** FHIR Consent resource propagation
- **Biosecurity:** Multi-layer sequence screening (IGS-compliant)
- **Cost:** Per-tenant affordability tier system
- **Biology AI:** Generative protein/DNA/RNA design adapters

## Directory Structure

```
openclinical-ai/
├── runtime/          # FastAPI inference server + multi-tenant runtime
├── registry/         # Signed model registry + manifest schema
├── consent/          # Patient consent engine
├── psw-assistant/    # PSW shift handoff assistant UI
├── biology_ai/       # Biology AI generation adapters
├── docs/             # Architecture, governance, compliance docs
├── tests/            # PyTest test suite
├── tenants/          # Tenant configuration
├── assets/           # Logos, banners
├── hf-space/         # Hugging Face Space deployment
├── examples/         # Runnable example scripts
└── .github/          # CI/CD workflows, dependabot
```

## Key Conventions

- Type hints everywhere (mypy strict mode)
- FastAPI Pydantic models for all request/response schemas
- Async endpoints with `await` throughout
- Multi-tenant isolation via `X-Tenant-ID` + `X-Tenant-API-Key` headers
- Audit logging on every inference, consent grant, and visit event
- Biosecurity screening on all generative biology endpoints
- `continue-on-error: false` in CI — all lint/format/security checks block PRs
- No hardcoded secrets — all config via environment variables (`OPENCLINICAL_*`)
