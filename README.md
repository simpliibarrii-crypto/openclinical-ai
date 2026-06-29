# openclinical-ai

**Open sovereign deployment substrate for biology AI and clinical AI in Canada.**

Apache 2.0 · [github.com/simpliibarrii-crypto/openclinical-ai](https://github.com/simpliabarrii-crypto/openclinical-ai)

---

## What this is

An open-source runtime for deploying clinical AI models (and biology AI models) with:

- **Sovereign inference** — runs in the same jurisdiction as patient data. No cloud round-trips.
- **Signed model registry** — every model artifact is Ed25519-signed; unsigned models rejected by default.
- **Audit gateway** — every inference logged in FHIR AuditEvent-compatible format.
- **Consent engine** — PHIPA-aligned opt-in consent, propagated to every call.
- **Voice-first PSW assistant** — shift-handoff demo at `/psw/`. No build step, no dependencies, runs in any modern browser.
- **Single-container deploy** — Docker, docker-compose, K8s-ready.

## Quickstart

### Run locally (60 seconds)

```bash
git clone https://github.com/simpliibarrii-crypto/openclinical-ai.git
cd openclinical-ai
python3 -m pip install 'fastapi>=0.110' 'uvicorn[standard]>=0.27' 'pydantic>=2.6' 'pynacl>=1.5' 'httpx>=0.27'

# Generate the demo signing key + signed model manifest
python3 tools/sign_manifest.py

# Start the runtime + voice UI
./run_dev.sh
```

Open http://localhost:8088 — the runtime redirects to the voice-first PSW shift-handoff assistant.

### Run with Docker

```bash
docker-compose up --build
```

Then open http://localhost:8088.

### Try the demo end-to-end

1. Open http://localhost:8088
2. Setup screen: PSW ID `psw-brian`, Resident ID `resident-001`, Runtime URL `http://localhost:8088`
3. Click **Grant consent & continue**
4. Fill in some vitals — e.g. `BP 145/90`, `HR 78`, `SpO2 89%`
5. Type or dictate a note — e.g. *"BP 145/90, walked 20m with walker, calm mood, daughter visited, refused morning meds"*
6. Click **Generate handoff summary**
7. Review the structured summary, flagged concerns, and audit ID

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  openclinical-ai runtime  (single container, sovereign)     │
├─────────────────────────────────────────────────────────────┤
│  PSW voice UI (/psw/)        ──┐                            │
│  Biology AI console  (TBD)    ──┤  HTTP                      │
│  Hospital EHR integration ────┤                            │
│                                ▼                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  FastAPI server                                      │    │
│  │  /health  /models  /v1/inference  /v1/consent/*      │    │
│  │  /audit/events                                        │    │
│  └─────────────────────────────────────────────────────┘    │
│       │              │              │              │          │
│       ▼              ▼              ▼              ▼          │
│  ┌────────┐    ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ Model  │    │ Consent  │   │  Audit   │   │ Registry │    │
│  │Runtime │◄──►│  Engine  │   │ Gateway  │   │ (signed) │    │
│  └────────┘    └──────────┘   └──────────┘   └──────────┘    │
│       │                                          │          │
│       ▼                                          ▼          │
│  Model adapters                  Ed25519-verified manifests │
│  - PSW shift handoff (heuristic) - psw-shift-handoff.v1.0.0  │
│  - biology protein fold (TBD)                                  │
│  - clinical NLP (TBD)                                         │
└─────────────────────────────────────────────────────────────┘
```

## What's in the box (MVP)

| Component | Path | Status |
|-----------|------|--------|
| Inference runtime | `runtime/server.py` | ✅ working |
| Signed model registry | `registry/`, `runtime/models.py` | ✅ working |
| Audit gateway | `runtime/audit.py` | ✅ working |
| Consent engine | `runtime/consent.py` | ✅ working |
| PSW voice-first UI | `psw-assistant/` | ✅ working |
| PSW shift-handoff adapter | `runtime/models.py:PSWShiftHandoffAdapter` | ✅ heuristic MVP |
| Signing tools | `tools/sign_manifest.py`, `tools/grant_consent.py` | ✅ working |
| Tests | `tests/test_substrate.py` | ✅ 20/20 pass |
| Dockerfile | `Dockerfile` | ✅ single container |
| docker-compose | `docker-compose.yml` | ✅ single-node + persistence |
| Model card schema | `registry/MODEL-CARD.md` | ⏳ draft |
| FHIR Consent integration | `fhir/` | ⏳ scaffolded |
| Biology AI adapters | `biology-ai/` | ⏳ scaffolded |
| K8s manifests | `deploy/` | ⏳ scaffolded |
| Compliance pack | `compliance/` | ⏳ scaffolded |

## What's coming

The MVP demonstrates the substrate architecture. The roadmap is to plug in real models:

1. **PSW shift-handoff** — replace heuristics with a fine-tuned clinical LLM trained on anonymized PSW shift notes
2. **Biology AI** — protein-folding adapter, variant-effect predictor, all running on Canadian sovereign compute (TamIA / Nibi / Trillium)
3. **Hospital integration** — FHIR R4 server adapter, SMART-on-FHIR auth, CDS Hooks
4. **Adversarial-robustness CI** — automated red-teaming of models before they're signed into the registry
5. **Edge tier** — Jetson Orin / Coral / Hailo deployment for retirement homes and remote clinics

## Why this matters

AlphaFold (UK), RoseTTAFold (US), ESM-3 (Meta US) — the foundational biology AI models are all foreign. Canadian biotech (AbCellera, Deep Genomics) is closed-source.

Clinical AI in Canadian hospitals runs on US vendor stacks (Epic Cosmos, Microsoft DAX, Nuance). PHIPA compliance is bolted on after the fact.

openclinical-ai is the open substrate everyone builds on:
- **Hospitals** deploy sovereign clinical AI without vendor lock-in
- **Researchers** publish models with signed provenance + audit trail
- **Patients** consent is propagated to every call, not just recorded
- **Citizens** Canadian genomic + clinical data stays in Canada

## License

Apache 2.0. See [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions require a CLA (signing over assignment of copyright to the project, with explicit license-back to Apache 2.0). This protects both contributors and downstream users.

---

**Built in Ottawa, for Canada, by a Personal Support Worker who knows what frontline care actually looks like.**