# openclinical-ai

Open substrate for clinical AI deployment.

Every hospital is reinventing the same thing: how to run clinical AI models safely, with audit trails, consent propagation, model provenance, and compliance artifacts. Every vendor locks it down. Every project ships without it.

This project solves it once, at the root, and gives it to everyone.

## What it is

An open-source monorepo providing the deployment substrate every clinical AI app depends on:

- **Inference runtime** — hardware-agnostic (CPU/GPU/edge), multi-model
- **Model registry** — signed, with provenance, model cards, drift monitoring
- **Audit gateway** — every inference logged, consent-aware, FHIR AuditEvent export
- **Consent engine** — patient consent propagated across the inference pipeline
- **Compliance pack** — pre-built artifacts for HIPAA / PHIPA / EU AI Act alignment
- **Deploy artifacts** — Kubernetes (cloud/on-prem), single-node (edge), Compose (dev)
- **FHIR-native** — SMART-on-FHIR auth, CDS Hooks, identity federation

## Why

The full research synthesis is in [`docs/PROJECT-BRIEF.md`](docs/PROJECT-BRIEF.md). Headline numbers:

- 1,451 FDA AI/ML device authorizations through 2025
- 41% of hospitals cite lack of model cards + drift documentation as their top AI audit barrier (Becker's Nov 2025)
- EU AI Act high-risk conformity assessments due **Aug 2026 / Aug 2027** as forcing function
- Epic holds ~70% of new hospital contracts; 60% of US beds on non-Epic — vendor-neutral alternative is the gap
- No open, cohesive, permissive, production-grade agentic + privacy + deployment stack exists

## Status

Pre-alpha. Building.

## Quick start

TBD — scaffold in progress.

## Architecture

```
openclinical-ai/
├── runtime/          # Inference runtime (CPU/GPU/edge), multi-model
├── registry/         # Signed model registry, provenance, model cards, drift monitoring
├── audit-gateway/    # Every inference logged, consent-aware, FHIR AuditEvent export
├── consent/          # Patient consent propagated across the inference pipeline
├── compliance/       # HIPAA / PHIPA / EU AI Act alignment artifacts (pre-built)
├── deploy/           # Kubernetes (cloud/on-prem), single-node (edge), Compose (dev)
├── fhir/             # FHIR-native identity, SMART-on-FHIR auth, CDS Hooks
└── docs/             # Project brief, threat model, regulator mapping
```

## Contributing

Open to collaborators. The substrate is too big for any one team. See [`docs/PROJECT-BRIEF.md`](docs/PROJECT-BRIEF.md) for the problem space. Reach out via issues.

## License

Apache 2.0. See [LICENSE](LICENSE).