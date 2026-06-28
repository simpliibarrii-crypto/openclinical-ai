# Project Brief — openclinical-ai

## Mission

Provide the open, standards-based deployment substrate every clinical AI app depends on, so any hospital — regardless of size, geography, or budget — can run clinical AI safely, with audit trails, consent propagation, model provenance, and compliance artifacts built in by default.

## The root problem

Across six parallel research streams (vendor landscape, cybersecurity, system unification, regulatory, open-source foundations, hardware/edge inference), the same gap surfaced under different names:

- **Cybersecurity brief:** "Clinical AI inference gateway + signed model registry + adversarial-robustness CI" is a greenfield infrastructure category — no incumbent owns it.
- **Open-source foundations:** "Missing layer is a cohesive, permissive, production-grade agentic + privacy + deployment stack." Four gaps identified:
  - (a) OSS clinical-AI agent runtime with audit and consent
  - (b) canonical hospital-on-K8s reference
  - (c) OSS confidential-computing primitives for clinical ML
  - (d) permissive-weight medical-imaging foundation models
- **Unification:** Epic holds ~70% of new hospital contracts; Cosmos has 300M+ records. 60% of US beds on non-Epic EHRs underserved. Vendor-neutral FHIR data fabric is the gap.
- **Vendor landscape:** 41% of hospitals cite lack of model cards + drift documentation as their top AI audit barrier (Becker's Nov 2025 CIO survey). HHS AI inventory deadline was Apr 2026 — now overdue.
- **Regulatory:** EU AI Act high-risk conformity assessments due Aug 2026 / Aug 2027. FDA PCCP standard now. HIPAA Security Rule update for AI training data.
- **Hardware:** Edge inference (Clara/Holoscan, OpenVINO, Hailo) + confidential compute (SGX, SEV, H100 CC) exists as components but no integrated open substrate ties them together.

## What we're building

An open-source monorepo providing the deployment substrate every clinical AI app depends on:

| Component | Purpose |
|---|---|
| `runtime/` | Inference runtime (CPU/GPU/edge), multi-model |
| `registry/` | Signed model registry, provenance, model cards, drift monitoring |
| `audit-gateway/` | Every inference logged, consent-aware, FHIR AuditEvent export |
| `consent/` | Patient consent propagated across the inference pipeline |
| `compliance/` | HIPAA / PHIPA / EU AI Act alignment artifacts (pre-built) |
| `deploy/` | Kubernetes (cloud/on-prem), single-node (edge), Compose (dev) |
| `fhir/` | FHIR-native identity, SMART-on-FHIR auth, CDS Hooks |
| `docs/` | Project brief, threat model, regulator mapping |

## Why now

- **EU AI Act** high-risk conformity assessments hit in **Aug 2026 / Aug 2027** — forcing function for compliance-by-default designs.
- **HHS AI inventory deadline** (Apr 2026) is now overdue — hospitals are scrambling for AI transparency tooling.
- **Epic dominance + 60% non-Epic underserved** creates structural gap for vendor-neutral alternatives.
- **No cohesive open substrate exists** — greenfield opportunity.

## Target users

- **Hospitals and health systems** — direct deployment, on-prem or cloud
- **Clinical AI vendors** — build on the substrate, get compliance for free
- **Researchers** — deploy research models to clinical environments without reinventing the wheel
- **Critical-access and rural hospitals** — run on edge hardware (Jetson-class) with the same compliance posture as large systems

## Built on

- **FHIR servers:** HAPI FHIR (2.4k★), Medplum (2.5k★)
- **Imaging AI:** MONAI (8.4k★), nnU-Net (8.6k★)
- **Federated learning:** NVIDIA FLARE, Flower (6.7k★)
- **Research data:** OHDSI/OMOP
- **Edge inference:** NVIDIA Clara/Holoscan, Intel OpenVINO, Hailo
- **Confidential compute:** Intel SGX, AMD SEV, NVIDIA H100/H200 CC

## Roadmap (initial 12 months)

- **Q3 2026:** Runtime + registry MVP. Basic inference + signed model loading + audit log.
- **Q4 2026:** FHIR integration. SMART-on-FHIR auth + consent engine + audit gateway.
- **Q1 2027:** Compliance pack. HIPAA / PHIPA / EU AI Act alignment artifacts.
- **Q2 2027:** Edge tier. Single-node deployment for resource-limited settings. Confidential compute integration.

## Open questions

- Reference EHR integration for testing — do we partner with Epic (via Cosmos-style API) or build against FHIR-only?
- Model registry — extend MLflow, or build on OCI/Docker distribution?
- Confidential compute — support NVIDIA H100 CC only, or also SGX/SEV?
- Edge target — Jetson Orin only, or also Coral, Hailo, Raspberry Pi?

## Contributing

Open to collaborators. The substrate is too big for any one team. Reach out via issues on this repo.