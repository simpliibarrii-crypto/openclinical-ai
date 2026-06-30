# Contributing

OpenClinical AI is a sovereign Canadian healthcare AI deployment substrate. Contributors play a vital role in advancing privacy-preserving, clinically-validated AI for Canadian healthcare systems. Your expertise helps build the foundation for trustworthy AI that respects patient privacy while delivering real clinical value.

## Before Opening a Pull Request

1. **Identify your contribution:** Open or reference an existing issue
2. **Minimize scope:** Keep changes focused and reviewable
3. **Add tests:** Include comprehensive test coverage
4. **Document changes:** Update relevant documentation
5. **Security review:** Consider privacy, security, and reproducibility impact

## Development Workflow

```bash
git checkout -b contribution/type-short-description
# Develop your feature

# Run the test suite for your changes
python -m pytest tests/ -q

# Additional tests if applicable
# npm test --if-present || true
# cargo test || true

# Review and commit changes
git add .
git commit -m "add/feature-description"
git push
```

**Testing Priority:** Always run `python -m pytest tests/ -v` before creating a PR.

## Code Standards

### Clinical Claims & Evidence
- All clinical assertions require supporting evidence
- Claims must include source citations or validation references
- Conservative interpretation: uncertainty is explicit, not hidden
- Machine-readable metadata accompanies all clinical data

### Security & Privacy
- Zero-trust architecture with least privilege access
- Explicit consent management for all PHI operations
- No hardcoded credentials, API keys, or tokens in source
- All network calls vetted for security implications
- Regular dependency vulnerability scanning

### Architecture & Modularity
- Small, focused, composable modules over monolithic abstractions
- Clear separation of concerns (runtime, governance, deployment)
- Explicit contracts and interfaces between components
- Configuration via structured files or environment variables
- Comprehensive error handling with privacy-safe logging

### Canadian Sovereignty
- Data residency compliance for Canadian deployments
- Integration with Canadian healthcare identifiers (PHIPPS, etc.)
- Compliance with PHIPA, HIPAA, and EU AI Act requirements
- Canadian cloud provider integration support (AWS Canada, GCP Canada)

### Testing & Validation
- Unit tests for all business logic and clinical decision support
- Integration tests for API contracts and data flows
- Security penetration testing for high-risk components
- Clinical validation studies for decision support recommendations
- Performance benchmarking for all deployment scenarios

## Code Structure Guidelines

### Runtime Components
```
openclinical-ai/
├── biology_ai/                    # Generative biology AI
├── consent/                      # Patient consent management
├── psw-assistant/                # PSW workflow automation  
├── runtime/                     # Core inference engine
│   ├── server.py                # API endpoints
│   ├── models.py                # Model registry and loading
│   ├── audit.py                 # Evidence trails
│   ├── efficient.py             # DeepSeek V4 routing
│   └── cost.py                   # Cost transparency
├── registry/                    # Signed model registry
├── tenants/                     # Multi-tenant identity & policy
├── docs/                        # Architecture, APIs, compliance
└── tests/                       # Comprehensive test suites
```

### Required Documentation
- API documentation (Auto-generated from server.py)
- Architecture diagrams (Architecture decisions documented)
- Clinical validation reports (Evidence for clinical claims)
- Security compliance matrices (Regulatory requirements)
- Performance benchmarks (Scalability testing)
- Migration guides (Production deployment)

## Clinical Validation Requirements

### For Clinical Decision Support
1. **Evidence Requirements:**
   - At least one peer-reviewed clinical study
   - Regulatory approval documentation (Health Canada, FDA, etc.)
   - Clinical guideline alignment documentation

2. **Safety Validation:**
   - Error rate validation (<0.1% for critical decisions)
   - Adverse event monitoring protocols
   - Fallback pathways for failed inferences

3. **Performance Standards:**
   - Response time <2 seconds for 95th percentile
   - Uptime >99.99% with proper monitoring
   - Cost transparency with per-tenant billing

## Security Standards

### Access Control
- Mutual TLS for all inter-service communication
- Role-based access control (RBAC) enforced
- Principle of least privilege across all layers
- Multi-factor authentication for administrative access

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3+ only)
- Data masking for development environments
- Secure key management (HSM integration)

### Compliance Documentation
- HIPAA Security Rule compliance matrices
- PHIPA (Alberta) compliance documentation
- EU AI Act high-risk category assessments
- Canadian Privacy Act compliance assertions

## Community Standards

### Communication
- Professional conduct in all interactions
- Respectful disagreement resolution
- Documentation of decisions and their rationale
- Open-source licensing compliance

### Collaboration
- Regular codebase reviews for security implications
- Peer review for all clinical claims and decisions
- Regular vulnerability disclosure processes
- Inclusive and welcoming community environment

## Acknowledgment

Your contribution to OpenClinical AI advances sovereign Canadian AI for healthcare. Together, we're building the foundation for trustworthy AI that respects patient privacy while delivering real clinical value to Canadian healthcare systems.
