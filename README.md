# openclinical-ai

**Open sovereign deployment substrate for biology AI and clinical AI in Canada. Multi-tenant by design — any healthcare service can connect, each tenant stays isolated.**

Apache 2.0 · [github.com/simpliabarrii-crypto/openclinical-ai](https://github.com/simpliabarrii-crypto/openclinical-ai)

---

## What this is

An open-source runtime for deploying clinical AI models (and biology AI models) with:

- **Sovereign inference** — runs in the same jurisdiction as patient data. No cloud round-trips.
- **Multi-tenant by design** — any healthcare service can connect, each tenant isolated with its own encryption keys, audit log, consent records, and rate limits.
- **Bring Your Own Key (BYOK)** — tenants bring their own KMS key (AWS KMS, Azure Key Vault, GCP KMS, HashiCorp Vault). openclinical-ai cannot decrypt PHI without tenant permission.
- **Signed model registry** — every model artifact is Ed25519-signed; unsigned models rejected by default.
- **Audit gateway** — every inference logged in FHIR AuditEvent-compatible format, tenant-scoped.
- **Consent engine** — PHIPA-aligned opt-in consent, propagated to every call.
- **Prompt-injection defense** — PSW free-text notes sanitized for 20+ injection patterns before AI inference. OWASP LLM01:2025 covered.
- **Voice-first home care UI** — visit documentation demo at `/psw/`. GPS check-in, family-visible notes, multi-visit/day, billing-ready timestamps.
- **Family portal** — read-only view of family-visible visit notes. No PHI. Separate token from PSW API key.
- **Single-container deploy** — Docker, docker-compose, K8s-ready.

## Multi-tenant architecture

```
┌─────────────────────────────────────────────────────────────┐
│  openclinical-ai runtime  (multi-tenant, sovereign)          │
├─────────────────────────────────────────────────────────────┤
│  Tenant A (Bayshore Ottawa)         Tenant B (Carefor Ottawa)│
│  ┌──────────────────────┐           ┌──────────────────────┐  │
│  │  Auth: per-tenant    │           │  Auth: per-tenant    │  │
│  │  BYOK: A's KMS key   │           │  BYOK: B's KMS key   │  │
│  │  Audit: per-tenant   │           │  Audit: per-tenant   │  │
│  │  Consent: per-tenant │           │  Consent: per-tenant │  │
│  │  Rate: per-tenant    │           │  Rate: per-tenant    │  │
│  └──────────────────────┘           └──────────────────────┘  │
│       │                                    │                 │
│       └────────────┬───────────────────────┘                 │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Shared hardened infrastructure                       │    │
│  │  - Signed model registry (Ed25519)                    │    │
│  │  - Audit gateway (FHIR AuditEvent-compatible)         │    │
│  │  - Consent engine (PHIPA-aligned)                     │    │
│  │  - Input sanitization (20+ injection patterns)        │    │
│  │  - mTLS + zero-trust (production)                     │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Defense-in-depth:** mTLS, zero-trust, per-tenant API keys (SHA-256 hashed), session tokens (8h TTL), Ed25519 model signatures, append-only audit logs, prompt-injection sanitization, BYOK encryption.

## Quickstart

### Run locally (60 seconds)

```bash
git clone https://github.com/simpliabarrii-crypto/openclinical-ai.git
cd openclinical-ai
python3 -m pip install 'fastapi>=0.110' 'uvicorn[standard]>=0.27' 'pydantic>=2.6' 'pynacl>=1.5' 'httpx>=0.27'

# Generate the demo signing key + signed model manifest
python3 tools/sign_manifest.py

# Start the runtime + voice UI
./run_dev.sh
```

Open http://localhost:8088 — the runtime redirects to the voice-first home care visit assistant.

### Run with Docker

```bash
docker-compose up --build
```

Then open http://localhost:8088.

### Try the demo end-to-end

1. Open http://localhost:8088 — pick your agency from the dropdown (Bayshore Ottawa, Carefor Ottawa, VHA Toronto)
2. Sign in as `psw-brian` (any PSW ID works for the demo)
3. See today's visits for that tenant (each tenant has its own visit list)
4. Click a visit → fill vitals + dictate notes → click **Generate visit summary**
5. See the structured summary + audit ID + sanitization report
6. Click **Family portal** to see what family caregivers see (read-only, sanitized)

### Smoke test the multi-tenant runtime

```bash
bash tools/smoke_test.sh
```

Verifies:
- `/health` returns version 0.2.0
- `/v1/tenants` returns 3 demo tenants
- Sign-in works for both `bayshore-ottawa` and `carefor-ottawa`
- Tenant A cannot see Tenant B's visits (isolation verified)
- Prompt-injection attempts are redacted + logged as `prompt-injection-blocked`
- GPS visit clock-in works with audit trail

## What's in the box (MVP v0.2.0)

| Component | Path | Status |
|-----------|------|--------|
| **Inference runtime** | `runtime/server.py` | ✅ working |
| **Multi-tenant registry** | `runtime/tenants.py` | ✅ 3 demo tenants |
| **Signed model registry** | `registry/`, `runtime/models.py` | ✅ Ed25519 verified |
| **Audit gateway** | `runtime/audit.py` | ✅ tenant-scoped |
| **Consent engine** | `runtime/consent.py` | ✅ PHIPA-aligned |
| **Input sanitization** | `runtime/sanitize.py` | ✅ 20+ injection patterns |
| **Voice-first UI** | `psw-assistant/` | ✅ home care visit docs |
| **Family portal** | `psw-assistant/` (family route) | ✅ read-only |
| **Visit lifecycle** | `runtime/server.py:/v1/visits/*` | ✅ clock-in/out + GPS |
| **PSW shift-handoff adapter** | `runtime/models.py:PSWShiftHandoffAdapter` | ✅ heuristic MVP |
| **Smoke test** | `tools/smoke_test.sh` | ✅ all endpoints |
| **Tests** | `tests/test_substrate.py` | ✅ 20/20 pass |
| **Dockerfile** | `Dockerfile` | ✅ single container |
| **docker-compose** | `docker-compose.yml` | ✅ persistence |
| **Threat model** | `docs/THREAT-MODEL.md` | ✅ STRIDE + multi-tenant |
| **Security policy** | `SECURITY.md` | ✅ multi-tenant scope |
| Model card schema | `registry/MODEL-CARD.md` | ⏳ draft |
| FHIR Consent integration | `fhir/` | ⏳ scaffolded |
| Biology AI adapters | `biology-ai/` | ⏳ scaffolded |
| K8s manifests | `deploy/` | ⏳ scaffolded |
| Compliance pack | `compliance/` | ⏳ scaffolded |

## API endpoints

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /health` | none | Runtime health + tenant count |
| `GET /models` | none | List loaded models (no secrets) |
| `GET /v1/tenants` | none | List tenants (no secrets) |
| `POST /v1/auth/signin` | none | Sign in PSW into tenant, get session token |
| `POST /v1/consent/grant` | none | Grant consent |
| `POST /v1/consent/revoke` | none | Revoke consent |
| `POST /v1/inference` | tenant | Run inference (sanitized, audited) |
| `GET /v1/visits/today` | tenant | PSW's visits for today |
| `GET /v1/visits/:id` | tenant | Visit details |
| `POST /v1/visits/clock-in` | tenant | GPS clock-in for visit |
| `POST /v1/visits/clock-out` | tenant | Finalize visit |
| `GET /v1/family/timeline` | family token | Family portal (read-only) |
| `GET /audit/events` | tenant | Tenant-scoped audit log |
| `GET /psw/` | none | PSW UI |

## What the home care wedge solves

Canadian home care agencies struggle with:
- **PSW documentation burden** — 30-45 min/visit of paperwork eats into care hours
- **Illegible handwriting** — paper records fail audit + care continuity
- **No real-time family visibility** — family caregivers rely on phone calls
- **No voice input** — every existing tool requires typed notes
- **GPS visit verification gaps** — billing disputes, missed visits
- **Multi-agency coordination** — clients often use 2-3 agencies; no shared record
- **PHIPA audit trail gaps** — most tools log "who accessed" but not "what was decided" by AI
- **Vendor lock-in** — proprietary data formats, can't extract your own clinical record

openclinical-ai:
- Voice-first PSW UI → less typing, faster documentation
- GPS visit verification → billing-audit-ready timestamps
- Family portal → real-time visibility without PHI leak
- Multi-tenant → each agency isolated, no cross-agency data flow
- Prompt-injection sanitization → PSW free-text can't extract other tenants' PHI
- FHIR-native → integrates with existing EHRs (planned)
- Apache 2.0 → no vendor lock-in

## What's coming

The MVP demonstrates the multi-tenant substrate architecture. The roadmap is to plug in real models + production hardening:

1. **Real PSW AI** — replace heuristic with fine-tuned clinical LLM trained on anonymized PSW visit notes
2. **Biology AI** — protein-folding adapter, variant-effect predictor, on Canadian sovereign compute (TamIA / Nibi / Trillium)
3. **Hospital integration** — FHIR R4 server adapter, SMART-on-FHIR auth, CDS Hooks
4. **Adversarial-robustness CI** — automated red-teaming of models before they're signed into the registry
5. **Edge tier** — Jetson Orin / Coral / Hailo deployment for retirement homes and remote clinics
6. **Compliance** — SOC 2 Type II (Year 1), ISO 27001 + 27018 (Year 1), HITRUST (Year 2), ISO/IEC 42001 (Year 2)

## Why this matters

AlphaFold (UK), RoseTTAFold (US), ESM-3 (Meta US) — the foundational biology AI models are all foreign. Canadian biotech (AbCellera, Deep Genomics) is closed-source.

Clinical AI in Canadian hospitals runs on US vendor stacks (Epic Cosmos, Microsoft DAX, Nuance). PHIPA compliance is bolted on after the fact.

Home care documentation runs on paper, Excel, or proprietary SaaS (AlayaCare, PointClickCare, CellTrak) — none of which is sovereign, voice-first, or family-portal-equipped.

openclinical-ai is the open substrate everyone builds on:
- **Home care agencies** deploy sovereign visit documentation without vendor lock-in
- **Hospitals** deploy sovereign clinical AI with PHIPA + Quebec Law 25 alignment
- **Researchers** publish models with signed provenance + audit trail
- **Patients** consent is propagated to every call, not just recorded
- **Citizens** Canadian genomic + clinical data stays in Canada

## License

Apache 2.0. See [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions require a CLA (signing over assignment of copyright to the project, with explicit license-back to Apache 2.0). This protects both contributors and downstream users.

---

**Built in Ottawa, for Canada, by a Personal Support Worker who knows what frontline care actually looks like.**