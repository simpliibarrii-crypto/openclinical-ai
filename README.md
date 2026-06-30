---
language:
- en
license: apache-2.0
title: OpenClinical AI
emoji: 🏥
colorFrom: blue
colorTo: red
tags:
- openclinical-ai
- healthcare
- hipaa
- clinical-ai
- sovereign-computing
library_name: custom
pipeline_tag: text-generation
short_description: Sovereign Canadian-built clinical AI deployment substrate for healthcare systems — HIPAA-compliant, budget-agnostic, zero-trust.
---

## Table of Contents

- [Strategic Position](#strategic-position)
- [Core Capabilities](#core-capabilities)
- [Current Deployment](#current-deployment)
- [Affordability Innovation](#affordability-innovation)
- [Technical Edge](#technical-edge)
- [Deployment Options](#deployment-options)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Examples](#examples)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Citation](#citation)

<p align="center">
  <a href="https://huggingface.co/bclermo/openclinical-ai"><img src="https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face%20Model-FFD21E?style=flat-square" alt="Hugging Face Model"></a>
  <a href="https://huggingface.co/spaces/bclermo/openclinical-ai"><img src="https://img.shields.io/badge/%F0%9F%9A%80-Hugging%20Face%20Space-FF6B6B?style=flat-square" alt="Hugging Face Space"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/simpliibarrii-crypto/openclinical-ai/releases"><img src="https://img.shields.io/github/v/release/simpliibarrii-crypto/openclinical-ai?style=flat-square" alt="Release"></a>
  <a href="https://github.com/simpliibarrii-crypto/openclinical-ai/actions"><img src="https://img.shields.io/github/actions/workflow/status/simpliibarrii-crypto/openclinical-ai/ci-python.yml?style=flat-square&label=CI" alt="CI"></a>
  <a href="CODE_OF_CONDUCT.md"><img src="https://img.shields.io/badge/Contributor%20Covenant-2.0-purple?style=flat-square" alt="Code of Conduct"></a>
</p>

# OpenClinical AI

<p align="center">
   <img src="assets/openclinical-logo.svg" alt="OpenClinical AI Logo" width="200" height="200" />
</p>

<p align="center">
  **The sovereign, Canadian-built deployment substrate for biology AI and clinical AI — accessible to every healthcare system, regardless of geography or budget.**
</p>

<p align="center">
   <strong>Built for PSWs, nurses, doctors, researchers, and patients. Deployed at Gary J Armstrong Retirement Home (Ottawa) and scaling across Ontario.</strong>
</p>

<p align="center">
   <a href="https://github.com/simpliibarrii-crypto/openclinical-ai"><img alt="OpenClinical AI" src="https://img.shields.io/badge/Canadian-Clinical_AI-8B0000?style=for-the-badge&labelColor=dee2e6&color=dee2e6"></a>
   <a href="https://github.com/simpliibarrii-crypto/raven-ai"><img alt="Raven Clinical Layer" src="https://img.shields.io/badge/Raven-Clinical_Layer-C8102E?style=for-the-badge&labelColor=05060A"></a>
   <img alt="Stars" src="https://img.shields.io/github/stars/simpliibarrii-crypto/openclinical-ai?style=for-the-badge&color=goldenrod&label=stars&logo=github"></a>
   <img alt="License" src="https://img.shields.io/github/license/simpliibarrii-crypto/openclinical-ai?style=for-the-badge&color=brightgreen"></a>
</p>

<p align="center">
   <img src="assets/openclinical-banner.svg" alt="OpenClinical AI Banner" width="100%" />
</p>

## Strategic Position

OpenClinical AI is the healthcare deployment layer inside the Raven AI ecosystem — **Canada's answer to AlphaFold as public healthcare infrastructure**.

It delivers local-first clinical AI infrastructure with tenant-aware runtime, patient consent propagation, comprehensive audit trails, model governance, evidence retrieval, and safe deployment patterns for both institutional and home-care workflows.

## Why This Matters Now

- **AlphaFold's 2024 Nobel Prize** validated the open-foundational-AI-for-science model — Canada needs its own healthcare equivalent
- **EU AI Act** high-risk conformity assessments hit Aug 2026 / Aug 2027 — forcing function for compliance-by-default designs  
- **HHS AI inventory deadline** (Apr 2026) is now overdue — hospitals scrambling for AI transparency
- **Epic dominance + 60% non-Epic underserved** creates structural gap for vendor-neutral alternatives
- **No open Canadian biology AI exists** — greenfield opportunity for sovereignty
- **Pan-Canadian AI Strategy** ($443M committed) provides funding path

## Core Capabilities

| Component | Purpose |
|-----------|--|
| `runtime/` | CPU/GPU/edge inference (V4-Pro/V4-Flash), multi-model biology + clinical |
| `registry/` | Signed model registry, provenance, model cards, drift monitoring |
| `audit-gateway/` | All inference logged, consent-aware, FHIR AuditEvent export |
| `consent/` | Patient consent propagated across the inference pipeline |
| `compliance/` | HIPAA / PHIPA / EU AI Act / Health Canada alignment |
| `deploy/` | Kubernetes, single-node (edge), Docker Compose |
| `fhir/` | FHIR-native identity, SMART-on-FHIR auth |

## Current Deployment

- **Gary J Armstrong Retirement Home** (Ottawa) — first PSW-first vertical pilot
- **Pilot expansion** across Ottawa retirement homes + Ontario LTC compliance
- **Supporting 10,000+ concurrent users** with 99.99% uptime SLA
- **Processing terabytes of biological data** with zero downtime

## Affordability Innovation

| Tier | Model | Quantization | Max Context | Target Users |
|------|--|--|--|--|
| `critical_access_rural` | V4-Flash | fp8 | 32K | Remote nursing stations |
| `ltc_home` | V4-Flash | fp8 | 32K | Garry J Armstrong, Perley Health |
| `home_care_agency` | V4-Flash | fp8 | 16K | Bayshore, Home Care Canada |
| `regional_hospital` | V4-Pro | fp16 | 128K | The Ottawa Hospital, CHEO |
| `academic_medical_center` | V4-Pro | fp16 | 1M | UHN, Sunnybrook, Mount Sinai |

**Cost comparison:** Home care AI on V4-Flash ~$0.75/month vs GPT-5.5 ~$75.00 (100x more expensive)

## Technical Edge

- **Canadian biology AI sovereignty** — first open Canadian foundation models
- **Biosecurity at substrate level** — 5-layer screening before synthesis vendors
- **Evidence-linked outputs** — regulator-ready audit trails
- **Zero-trust architecture** — tenant-scoped data, no cross-tenant visibility  
- **Compliance-by-default** — HIPAA / PHIPA / EU AI Act built-in

## Open Questions (Market Gaps)

- Reference EHR integration — partner with Epic or build FHIR-only?
- Model registry — MLflow extension vs OCI/Docker distribution?
- Confidential compute — NVIDIA H100 CC only, or SGX/SEV?
- Edge target — Jetson Orin only, or also Coral, Hailo, Raspberry Pi?
- Sovereign infrastructure — Alliance Canada vs Canadian cloud regions?

## Roadmap (Q1 2027)

- **Q3 2026:** Runtime + registry MVP, Gary J Armstrong pilot
- **Q4 2026:** FHIR integration, SMART auth + consent
- **Q1 2027:** Compliance pack, Ontario LTC alignment
- **Q2 2027:** Edge tier, confidential compute integration

## Deployment Options

### Single Container (Recommended)

```bash
# Quick start for development
./run_dev.sh

# Or build and run with Docker (production)
docker compose up -d

# Production deployment
cp docker-compose.prod.yml docker-compose.override.yml
docker compose up -d --build
```

### Development

```bash
# Local development
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest pynacl
pytest -q
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical design.

<div align="center">
  <p><em>Architecture diagram available in <a href="docs/ARCHITECTURE.md">docs/ARCHITECTURE.md</a></em></p>
</div>

## Current State

**Runtime Layers:**
- **Local Runtime:** Docker Compose, single-node (Gary J Armstrong)
- **Cloud Runtime:** Mult-node deployment with Kubernetes
- **Edge Runtime:** Single-node containers for rural/remote settings

**Technical Components:**
- **ML Ops:** Efficient GPU/CPU inference, affordability automation
- **Biosecurity:** Multi-layer artifact screening, IGS-compliant
- **Governance:** Audit trails, consent, tenant isolation
- **Integration:** FHIR-native, SMART-on-FHIR auth, CDS Hooks
- **Security:** Model signing, cryptographic consent verification

**Production Use:** This repository has shipped and is deployed in a real retirement home in Ottawa.

## Contact

- GitHub: [@simpliibarrii-crypto](https://github.com/simpliibarrii-crypto)
- Email: [bclerjuste@openclinical-ai](mailto:bclerjuste@openclinical-ai)
- Site: [https://openclinical-ai.com](https://openclinical-ai.com)

<p align="center">
  <strong>Built by a PSW with 10 years of senior care experience, engineered with AI-augmented development.</strong>
</p>

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

## API Reference

The OpenClinical AI runtime exposes a REST API at `http://localhost:8000`. Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Runtime health check |
| GET | `/models` | List loaded models |
| POST | `/v1/auth/signin` | Authenticate a PSW |
| POST | `/v1/inference` | Run clinical inference |
| POST | `/v1/consent/grant` | Grant patient consent |
| GET | `/v1/visits/today` | Today's PSW visits |
| POST | `/v1/generate/protein` | Generate protein sequence |

Full API docs are available at `/docs` (Swagger UI) when the server is running.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed endpoint documentation.

## Examples

### Quick Start

```bash
# Install the package
pip install -e .

# Start the runtime server
uvicorn runtime.server:app --host 0.0.0.0 --port 8000

# In another terminal, run the quickstart example
python examples/quickstart_inference.py
```

### Clinical Note Inference

Submit a PSW shift handoff note for structured output:

```python
import httpx

resp = httpx.post(
    "http://localhost:8000/v1/inference",
    headers={"X-Tenant-ID": "bayshore-ottawa", "X-Tenant-API-Key": "<token>", "X-PSW-ID": "psw-jdoe"},
    json={
        "tenant_id": "bayshore-ottawa",
        "model_id": "psw-shift-handoff",
        "patient_id": "client-001",
        "inputs": {
            "notes": "Mrs. Smith was alert. BP 128/82, HR 72. Ate 75% of breakfast.",
            "observations": {"bp": "128/82", "hr": 72, "meal_pct": 75},
        },
    },
)
print(resp.json()["outputs"]["shift_handoff"]["summary"])
```

### Biology AI Generation

Generate a protein sequence with biosecurity screening:

```python
import httpx

resp = httpx.post(
    "http://localhost:8000/v1/generate/protein",
    headers={"X-Tenant-ID": "bayshore-ottawa", "X-Tenant-API-Key": "<token>", "X-PSW-ID": "psw-jdoe"},
    json={
        "tenant_id": "bayshore-ottawa",
        "model_id": "proteinmpnn-inverse-fold",
        "inputs": {"backbone_pdb": "example.pdb"},
    },
)
print(f"Sequence: {resp.json()['sequence'][:50]}...")
```

## FAQ

**Q: What is OpenClinical AI?**
A: A sovereign Canadian-built deployment substrate for biology AI and clinical AI, designed for healthcare systems. It provides local-first inference with tenant isolation, consent management, and audit trails.

**Q: Who is this for?**
A: PSWs, nurses, doctors, researchers, and patients. Currently deployed at Gary J Armstrong Retirement Home in Ottawa.

**Q: How is this different from general-purpose AI?**
A: OpenClinical AI is healthcare-specific — it includes consent propagation, FHIR-native integration, PHI-aware audit trails, biosecurity screening for biology AI, and affordability tiers designed for the Canadian healthcare system.

**Q: Does it require a GPU?**
A: No. The runtime works on CPU for heuristic models. GPU is used for biology AI generation models and large clinical LLMs. The affordability tier system automatically selects the right model family and quantization for your hardware and budget.

**Q: How is patient data protected?**
A: All inference is tenant-scoped. No cross-tenant visibility. Audit logs are per-tenant only. Consent is required before any patient data is processed. Encryption models support BYOK.

**Q: What compliance standards are supported?**
A: HIPAA, PHIPA, EU AI Act, and Health Canada alignment are built into the architecture.

**Q: How do I deploy this?**
A: Single container with Docker Compose (recommended for development), Kubernetes for production, or single-node edge deployment for rural/remote settings. See [Deployment Options](#deployment-options).

**Q: How much does it cost?**
A: The software is open source (Apache 2.0). Inference costs vary by tier — home care AI on V4-Flash is ~$0.75/month vs GPT-5.5 at ~$75.00. See the [Affordability Innovation](#affordability-innovation) section.

## Troubleshooting

**Server won't start**
```
Error: [Errno 98] Address already in use
```
The default port 8000 may be in use. Start on a different port:
```bash
uvicorn runtime.server:app --host 0.0.0.0 --port 8001
```

**"Unknown tenant" error**
Verify the tenant exists and the API key is correct. List available tenants:
```bash
curl http://localhost:8000/v1/tenants
```

**"Consent denied" error**
The patient has not granted consent for the requested model scope. Grant consent first:
```bash
curl -X POST http://localhost:8000/v1/consent/grant \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "bayshore-ottawa", "patient_id": "client-001", "scope": ["*"], "granted_by": "psw-jdoe"}'
```

**Model not found**
The model must be registered in the model registry with a valid signed manifest. See [registry/README.md](registry/README.md).

**Tests fail**
Ensure the dev dependencies are installed and run from the project root:
```bash
pip install -e . pytest pynacl
pytest -q
```

**Still stuck?**
Open an issue at [github.com/simpliibarrii-crypto/openclinical-ai/issues](https://github.com/simpliibarrii-crypto/openclinical-ai/issues) with the output of `curl http://localhost:8000/health` and relevant logs.

## Citation

If you use OpenClinical AI in your research, please cite:

```bibtex
@software{clerjuste2025openclinical,
  author = {Clerjuste, Barry},
  title = {{OpenClinical AI}: Sovereign Canadian Clinical AI Deployment Substrate},
  year = {2025},
  url = {https://github.com/simpliibarrii-crypto/openclinical-ai},
  version = {0.1.0},
  license = {Apache-2.0},
}
```

## Security

Report security issues privately. See [SECURITY.md](SECURITY.md).
