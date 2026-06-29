# Threat Model — openclinical-ai

Starting STRIDE-style analysis. Living document.

**Current version:** v0.2.0 (multi-tenant, home-care pivot)

## Assets

- **Patient health information (PHI)** flowing through inference pipeline
- **Model weights** in the registry (signing, provenance)
- **Audit logs** (tamper-resistance)
- **Consent records** (patient-controlled)
- **Inference results** (returned to calling systems)
- **Tenant isolation boundaries** (multi-tenant: agency-byok, audit, consent per tenant)
- **Tenant API keys + session tokens** (auth for per-tenant access)
- **Family-visible visit notes** (read-only, sanitized)
- **GPS visit verification data** (PHI under PHIPA)

## Trust boundaries

1. **External → API:** Clinical apps + family portal calling endpoints
2. **API → runtime:** Request validation, auth, consent check, sanitization
3. **Runtime → registry:** Model loading, Ed25519 signature verification
4. **Runtime → tenant registry:** Tenant lookup, encryption-model routing
5. **Runtime → audit gateway:** Tenant-scoped inference + visit events
6. **Runtime → consent engine:** Tenant-scoped consent check
7. **Runtime → response:** Sanitized results back to caller (no cross-tenant data)
8. **Tenant A ↔ Tenant B:** STRICT ISOLATION — no data flow, no shared process
9. **Audit gateway → external storage:** Long-term audit (FHIR server, S3) per tenant

## Threats (STRIDE)

### Spoofing

- **T-S1:** Forged model weight uploaded to registry
  - *Mitigation:* Ed25519-signed manifests (verified on load), SHA-256 hash pinning, registry mounted RO at runtime
- **T-S2:** Forged caller identity hitting inference API
  - *Mitigation:* Per-tenant API keys (SHA-256 hashed in storage), session tokens with 8h TTL, PSW ID in header
- **T-S3:** Forged session token (replay or stolen)
  - *Mitigation:* Session expiry, server-side session table, tenant_id + psw_id binding in session
- **T-S4:** Cross-tenant token reuse (Bayshore token used to hit Carefor)
  - *Mitigation:* Session record stores tenant_id; require_tenant() validates token's tenant_id matches X-Tenant-ID header

### Tampering

- **T-T1:** Audit log tampered after the fact
  - *Mitigation:* Append-only JSONL storage, hash chaining, periodic anchoring to immutable store
- **T-T2:** Model weights swapped at runtime
  - *Mitigation:* Ed25519 signature verification on load, registry mounted RO in container
- **T-T3:** Inference result tampered in transit
  - *Mitigation:* TLS, signed responses, response verification at caller
- **T-T4:** Tenant API key leaked
  - *Mitigation:* Keys stored hashed (SHA-256), plaintext shown once at creation, rotate via API; tenant can self-revoke

### Repudiation

- **T-R1:** Hospital denies a clinical decision was made by AI
  - *Mitigation:* Full audit trail with model version, input snapshot (sanitized), output, operator identity, tenant_id
- **T-R2:** PSW denies a visit was completed
  - *Mitigation:* GPS clock-in/clock-out events with lat/lng + timestamp, audit event IDs returned to UI

### Information disclosure

- **T-I1:** PHI leakage via prompt injection
  - *Mitigation:* Pre-inference sanitization (20+ injection patterns), structured prompting, output validation, audit-logged `prompt-injection-blocked` events
- **T-I2:** PHI leakage via inference timing attacks
  - *Mitigation:* Constant-time inference, batching, no per-tenant timing variance
- **T-I3:** Model inversion attack (recover training data from model)
  - *Mitigation:* Differential privacy during training, output perturbation, model adapter sandboxing
- **T-I4:** Registry enumeration
  - *Mitigation:* Authenticated registry access, audit on enumeration, public `/models` returns IDs + descriptions only
- **T-I5:** Cross-tenant data leakage (Tenant A's PSW sees Tenant B's visits)
  - *Mitigation:* `require_tenant()` dependency on every protected endpoint, visit queries filter by `tenant_id == ctx.tenant_id`, audit queries filter by `tenant_id`, per-tenant encryption keys (BYOK)
- **T-I6:** Family portal sees PHI instead of family-visible notes
  - *Mitigation:* Family portal uses separate token (not the PSW API key), endpoint returns only `family_visible_note` field with PHI sanitization
- **T-I7:** PSW free-text notes leak PHI into AI inference
  - *Mitigation:* `sanitize_free_text()` strips SSN/SIN/PHN patterns, max-length cap (32K chars), redacted substrings logged
- **T-I8:** Family-visible note accidentally contains clinical detail
  - *Mitigation:* Sanitization on store (separate from inference sanitization), structured input field, length cap (1K chars)
- **T-I9:** Tenant API key transmitted in cleartext
  - *Mitigation:* TLS required, CORS allowlist, server-side only over HTTPS in production

### Denial of service

- **T-D1:** Inference endpoint flooded
  - *Mitigation:* Rate limiting per tenant (planned), queue depth caps, circuit breakers per model
- **T-D2:** Expensive model triggered by low-priority caller
  - *Mitigation:* Tiered model access (planned), quota per tenant
- **T-D3:** Noisy-neighbor attack (Tenant A consumes resources, Tenant B suffers)
  - *Mitigation:* Per-tenant rate limits + resource quotas (planned), container-level isolation in production

### Elevation of privilege

- **T-E1:** Inference caller gets write access to audit log
  - *Mitigation:* Separate auth domains; audit gateway is write-only from caller perspective; audit query requires tenant_id (no "list all")
- **T-E2:** Compromised model gets network access at runtime
  - *Mitigation:* Sandboxed inference (gVisor, Firecracker), no network egress by default, model adapter pattern keeps model code isolated
- **T-E3:** Cross-tenant privilege escalation
  - *Mitigation:* `require_tenant()` rejects unknown tenant_ids, API key lookup validates hashed match, session token tenant binding
- **T-E4:** PSW gains tenant-admin privileges
  - *Mitigation:* PSW session tokens have no admin scope; tenant admin actions require separate auth (planned for v1)
- **T-E5:** Inference caller bypasses consent check
  - *Mitigation:* Consent check is non-optional in inference pipeline; missing/expired token → `consent-denied` event + HTTP 403

## Multi-tenant isolation model

**Architecture:** Hybrid silo + pool. Default = schema-per-tenant (per-tenant JSONL audit, per-tenant consent records). Silo mode available for high-security tenants (provincial health authorities, hospitals) with their own KMS key.

```
┌──────────────────────────────────────────────────────────────┐
│  openclinical-ai multi-tenant runtime                        │
├──────────────────────────────────────────────────────────────┤
│  Tenant A (Bayshore Ottawa)        Tenant B (Carefor Ottawa) │
│  ┌──────────────────────┐          ┌──────────────────────┐  │
│  │  Auth (OIDC + MFA)   │          │  Auth (OIDC + MFA)   │  │
│  │  BYOK: A's KMS key   │          │  BYOK: B's KMS key   │  │
│  │  Schema: bayshore_*  │          │  Schema: carefor_*   │  │
│  │  Audit: bayshore.log │          │  Audit: carefor.log  │  │
│  │  Consent: FHIR R4    │          │  Consent: FHIR R4    │  │
│  │  Model: signed       │          │  Model: signed       │  │
│  │  Rate: 100 req/s     │          │  Rate: 50 req/s      │  │
│  └──────────────────────┘          └──────────────────────┘  │
│       │                                    │                 │
│       └────────────┬───────────────────────┘                 │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Shared infrastructure (hardened)                     │    │
│  │  - mTLS everywhere                                   │    │
│  │  - Zero-trust                                        │    │
│  │  - Per-tenant rate limits + quotas (planned)         │    │
│  │  - Per-tenant resource isolation                     │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Defense-in-depth layers:**
1. Network — mTLS, zero-trust (planned)
2. Identity — per-tenant API keys (hashed), session tokens, PSW ID binding
3. Data — BYOK encryption, tenant-scoped queries
4. Compute — process-level isolation (planned: container-per-tenant silo mode)
5. Model — Ed25519 signed manifests, no network egress
6. Audit — per-tenant immutable log, FHIR AuditEvent export
7. Input — sanitization + prompt injection defense + structured prompting
8. Output — PHI redaction, family-visible sanitization, content classifiers (planned)

## Cross-cutting

- **Supply chain:** All dependencies pinned + signed (sigstore/cosign planned). Model weights Ed25519-signed + provenance verified.
- **AI-specific:** OWASP LLM Top 10 (2025) covered — prompt injection (T-I1), training data poisoning (T-I3), model DoS (T-D1, T-D2), supply chain (T-S1, T-T2). NIST AI RMF mapping in `docs/REGULATORY-MAPPING.md`.
- **Adversarial robustness:** Prompt-injection patterns catalogued in `runtime/sanitize.py`; injection attempts logged as `prompt-injection-blocked` audit events. Real clinical AI models must pass adversarial-robustness CI (planned).
- **Healthcare breach lessons (Change Healthcare 2024):**
  - One Citrix server without MFA → $2.9B+ impact
  - Lesson: MFA mandatory, network segmentation, immutable backups, kill switch
  - openclinical-ai: mandatory session expiry, tenant-scoped audit, append-only storage

## Compliance roadmap

| Framework | Status | Target |
|-----------|--------|--------|
| PHIPA technical safeguards (Ontario) | MVP aligned | Year 1 |
| Quebec Law 25 | MVP aligned | Year 1 |
| PIPEDA | MVP aligned | Year 1 |
| SOC 2 Type II | Planned | Year 1 |
| NIST CSF 2.0 | MVP aligned | Year 1 |
| ISO 27001 + 27018 | Planned | Year 1 |
| NIST AI RMF | Planned | Year 1 |
| HITRUST CSF | Planned | Year 2 |
| ISO/IEC 42001 (AI mgmt) | Planned | Year 2 |

## Out of scope (for now)

- Network-level attacks (DDoS at L3/L4) — handled by infra layer
- Physical security of hospital data centers — handled by hospital
- Insider threat from hospital staff with legitimate access — handled by hospital IAM
- Patient-side social engineering — handled by patient education
- Quantum-resistant cryptography — planned for v2 (when NIST PQC standards final)