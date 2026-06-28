# Threat Model — openclinical-ai

Starting STRIDE-style analysis. Living document.

## Assets

- **Patient health information (PHI)** flowing through inference pipeline
- **Model weights** in the registry (signing, provenance)
- **Audit logs** (tamper-resistance)
- **Consent records** (patient-controlled)
- **Inference results** (returned to calling systems)

## Trust boundaries

1. **External → API:** Clinical apps calling inference endpoints
2. **API → runtime:** Request validation, auth, consent check
3. **Runtime → registry:** Model loading, signature verification
4. **Runtime → audit gateway:** Inference events
5. **Runtime → response:** Results back to caller
6. **Audit gateway → external storage:** Long-term audit (FHIR server, S3, etc.)

## Threats (STRIDE)

### Spoofing

- **T-S1:** Forged model weight uploaded to registry
  - *Mitigation:* Signed model artifacts (cosign/Sigstore), provenance attestation (SLSA), registry-side verification before model is loadable
- **T-S2:** Forged caller identity hitting inference API
  - *Mitigation:* SMART-on-FHIR auth, mTLS, JWT with short TTL

### Tampering

- **T-T1:** Audit log tampered after the fact
  - *Mitigation:* Append-only storage, hash chaining, periodic anchoring to immutable store
- **T-T2:** Model weights swapped at runtime
  - *Mitigation:* Registry-side verification on load, runtime integrity check
- **T-T3:** Inference result tampered in transit
  - *Mitigation:* TLS, signed responses, response verification at caller

### Repudiation

- **T-R1:** Hospital denies a clinical decision was made by AI
  - *Mitigation:* Full audit trail with model version, input snapshot, output, operator identity

### Information disclosure

- **T-I1:** PHI leakage via prompt injection
  - *Mitigation:* Output filtering, PHI redaction, model-side constraints
- **T-I2:** PHI leakage via inference timing attacks
  - *Mitigation:* Constant-time inference, batching
- **T-I3:** Model inversion attack (recover training data from model)
  - *Mitigation:* Differential privacy during training, output perturbation
- **T-I4:** Registry enumeration
  - *Mitigation:* Authenticated registry access, audit on enumeration

### Denial of service

- **T-D1:** Inference endpoint flooded
  - *Mitigation:* Rate limiting per caller, queue depth caps, circuit breakers
- **T-D2:** Expensive model triggered by low-priority caller
  - *Mitigation:* Tiered model access, quota per role

### Elevation of privilege

- **T-E1:** Inference caller gets write access to audit log
  - *Mitigation:* Separate auth domains, audit gateway is write-only from caller perspective
- **T-E2:** Compromised model gets network access at runtime
  - *Mitigation:* Sandboxed inference (gVisor, Firecracker), no network egress by default

## Cross-cutting

- **Supply chain:** All dependencies pinned + signed (sigstore/cosign). Model weights signed + provenance verified.
- **AI-specific:** OWASP LLM Top 10 (2025) covered. NIST AI RMF mapping in `docs/REGULATORY-MAPPING.md`.
- **Adversarial robustness:** Adversarial inputs (FGSM, PGD) validated at CI; model outputs filtered for known attack signatures.

## Out of scope (for now)

- Network-level attacks (DDoS at L3/L4) — handled by infra layer
- Physical security of hospital data centers — handled by hospital
- Insider threat from hospital staff with legitimate access — handled by hospital IAM