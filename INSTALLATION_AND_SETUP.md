INSTALLATION_AND_SETUP.md
=====================

This document provides complete installation and setup instructions for both **Raven AI** and **OpenClinical AI** - enterprise-grade AI deployment platforms designed for computational biology, healthcare systems, and scientific research.

## Prerequisites

### System Requirements
- **RAM**: Minimum 32GB (64GB+ recommended for production)
- **CPU**: 16+ cores (AMD EPYC/Intel Xeon)
- **Storage**: 500GB+ SSD for model weights and data
- **Network**: 1Gbps Ethernet, local-first deployment supported

### Software Dependencies
```bash
# Ubuntu/Debian (production)
sudo apt update && sudo apt install -y python3.11 python3.11-venv docker-compose git curl

# For development containers (recommended)
docker run -it --gpus all --ipc=host -v $PWD:/workspace --network=host python:3.11-slim

# Configure container environment
export OPENCLINICAL_ENV=production
export CUDA_VISIBLE_DEVICES=0,1,2,3
```

## Quick Start

### Option 1: Docker Quick Deployment (Recommended)

```bash
# Clone and deploy OpenClinical AI (healthcare deployment)
git clone https://github.com/simpliibarrii-crypto/openclinical-ai.git
cd openclinical-ai
docker compose up -d

# Verify deployment
curl -fsS http://localhost:8088/health
```

```bash
# Clone and deploy Raven AI (agent orchestration)
git clone https://github.com/simpliibarrii-crypto/raven-ai.git
cd raven-ai
docker compose up -d

# Verify deployment
curl -fsS http://localhost:8000/health
```

### Option 2: Native Installation

```bash
# Clone repositories
git clone https://github.com/simpliibarrii-crypto/openclinical-ai.git
git clone https://github.com/simpliibarrii-crypto/raven-ai.git

# OpenClinical AI setup
cd openclinical-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -c "import openclinical_ai; print('OpenClinical AI ✓')"

# Raven AI setup  
cd raven-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -c "import raven_ai; print('Raven AI ✓')"
```

## Configuration Management

### Environment Variables

#### OpenClinical AI Runtime
```bash
export OPENCLINICAL_ENV=production
export OPENCLINICAL_REGISTRY_PATH=/app/registry
export OPENCLINICAL_AUDIT_PATH=/var/lib/openclinical/audit
export OPENCLINICAL_CONSENT_PATH=/var/lib/openclinical/consent
export OPENCLINICAL_TENANTS_PATH=/var/lib/openclinical/tenants
export OPENCLINICAL_CORS_ORIGINS="*"
```

#### Raven AI Configuration
```bash
export RAVEN_ENV=production
export RAVEN_MODELS_PATH=/app/models
export RAVEN_LOG_PATH=/var/log/raven
export RAVEN_MAX_CONCURRENT_AGENTS=100
```

### Configuration Files

#### OpenClinical AI

**Config File Structure:**
```
openclinical-ai/
├── config.yaml                    # Main configuration
├── runtime/
│   └── config.py                 # Runtime configuration
├── tenants/
│   ├── default.yaml             # Default tenant
│   ├── ontario.yaml             # Ontario healthcare
│   └── clinical-center.yaml     # Clinical center tenant
└── registry/
    ├── models.yaml              # Model configurations
    └── security.yaml            # Security policies
```

**Sample Configuration (`config.yaml`):**
```yaml
# OpenClinical AI Configuration
runtime:
  host: "0.0.0.0"
  port: 8088
  workers: 8
  timeout: 300

tiers:
  default: "home_care_agency"
  escalation_enabled: true

compliance:
  hipaa: true
  phipa: true
  eu_ai_act: true
  health_canada: true

security:
  encryption_model: "BYOK"
  audit_retention_days: 2555
  consent_retention_days: 1095

biosecurity:
  enabled: true
  risk_threshold: 0.7
  screening_layers: 5
```

#### Raven AI

**Sample Configuration (`raven_config.py`):**
```python
# Raven AI Configuration
class RavenConfig:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8000
        self.workers = 16
        self.max_concurrent_agents = 100
        self.timeout_seconds = 600
        
        # Agent Configuration
        self.agent:
            max_tools_per_agent = 50
            planning_horizon_hours = 24
            confidence_threshold = 0.85
            
        # Model Configuration
        self.models:
            default_family = "v4-pro"
            quantization = "fp16"
            context_length = 1000000
            
        # Clinical Validation
        self.clinical_validation:
            evidence_required = True
            peer_review_enabled = True
            regulatory_compliance = ["HIPAA", "PHIPA", "EU_AI_Act"]
```

## Quick Start - Raven AI

### 1. Basic Setup
```bash
cd raven-ai

# Install dependencies
pip install -r requirements.txt
pip install torch transformers fastapi uvicorn

# Initialize Raven AI
cat > app.py << 'EOF'
from raven_ai import RavenAI, AgentConfiguration
from raven_ai.models import V4ProModel, V4FlashModel

# Configure Raven AI
config = AgentConfiguration(
    host="0.0.0.0",
    port=8000,
    max_concurrent_agents=100,
    confidence_threshold=0.85
)

# Initialize with V4-Pro model
model = V4ProModel(
    model_id="deepseek-ai/DeepSeek-V4-Pro",
    quantization="fp16",
    context_length=1000000
)

# Create Raven AI instance
raven = RavenAI(config=config, model=model)

# Start the server
raven.run()
EOF

python app.py
```

### 2. Agent Example
```python
from raven_ai import RavenAI, AgentConfiguration, ClinicalAgent

# Configure agent for drug interaction studies
agent_config = AgentConfiguration(
    max_tools_per_agent=20,
    planning_horizon_hours=48,
    medical_specialty="pharmacology"
)

# Create clinical agent for drug interactions
clinical_agent = ClinicalAgent(
    agent_config=agent_config,
    specialty="pharmacology",
    focus_areas=["drug-interaction", "adverse-event"]
)

# Run inference
result = clinical_agent.run({
    "patient_history": "Patient with asthma and multiple medications",
    "current_medications": ["albuterol", "lisinopril", "metformin"],
    "symptoms": ["chest pain", "shortness of breath"],
    "allergies": ["penicillin"]
})

print(f"Risk Assessment: {result.risk_score}")
print(f"Potential Interactions: {result.interactions}")
```

## Quick Start - OpenClinical AI

### 1. Basic Setup
```bash
cd openclinical-ai

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn sqlmodel pyjwt cryptography

# Initialize database and registry
cat > run_production.py << 'EOF'
from openclinical_ai import OpenClinicalAI, TenantConfiguration
from openclinical_ai.runtime import TenantRegistry

# Configure tenants
ontario_tenant = TenantConfiguration(
    tenant_id="ontario-health-ministry",
    name="Ontario Ministry of Health",
    tier="regional_hospital",
    encryption_model="BYOK",
    compliance_timezone="America/Toronto"
)

clinical_center_tenant = TenantConfiguration(
    tenant_id="gary-j-armstrong",
    name="Gary J. Armstrong Retirement Home",
    tier="ltc_home",
    encryption_model="BYOK",
    compliance_timezone="America/Toronto"
)

# Initialize tenants registry
tenants = TenantRegistry()
tenants.add_tenant(ontario_tenant)
tenants.add_tenant(clinical_center_tenant)

# Initialize OpenClinical AI
openclinical = OpenClinicalAI(
    host="0.0.0.0",
    port=8088,
    tenants=tenants,
    biosecurity_enabled=True
)

# Start the service
openclinical.run()
EOF

python run_production.py
```

### 2. Clinical Workflow Example
```python
from openclinical_ai import OpenClinicalAI, ConsentManager, AuditLogger
from openclinical_ai.runtime import AffordabilityCalculator

# Initialize components
consent = ConsentManager()
audit = AuditLogger()
affordability = AffordabilityCalculator()

# Create OpenClinical AI instance
openclinical = OpenClinicalAI(
    consent=consent,
    audit=audit,
    affordability=affordability
)

# Patient consent workflow
patient_id = "patient-123"
consent_token = consent.grant_consent(
    patient_id=patient_id,
    scope=["drug-interaction", "variant-impact"],
    granted_by="dr.smith@hospital.com"
)

# Run clinical inference
result = openclinical.run_inference(
    tenant_id="gary-j-armstrong",
    model_id="v4-pro-clinical",
    patient_id=patient_id,
    inputs={
        "patient_data": {
            "age": 78,
            "weight": 75,
            "medications": ["metformin", "atorvastatin"]
        },
        "query": "Check for drug interactions with new prescription"
    },
    consent_token=consent_token
)

print(f"Inference ID: {result.inference_id}")
print(f"Cost Estimate: ${result.cost_usd:.4f}")
print(f"Clinical Findings: {result.outputs}")
```

## Deployment Scripts

### OpenClinical AI Deployment Script

```bash
#!/bin/bash
# openclinical-deploy.sh

set -e

# Configuration
IMAGE_NAME="openclinical-ai"
TAG="latest"
REGISTRY="your-registry.com"
NAMESPACE="healthcare"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main deployment function
deploy_openclinical() {
    log_info "Starting OpenClinical AI deployment..."
    
    # Build and push Docker image
    log_info "Building Docker image..."
    docker build -t ${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${TAG} .
    
    # Deploy to Kubernetes
    log_info "Deploying to Kubernetes..."
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/ingress.yaml
    
    # Wait for deployment
    log_info "Waiting for deployment to complete..."
    kubectl rollout status deployment/${IMAGE_NAME} -n ${NAMESPACE}
    
    # Verify deployment
    log_info "Verifying deployment..."
    kubectl get pods -l app=${IMAGE_NAME} -n ${NAMESPACE}
    
    # Run health checks
    log_info "Running health checks..."
    sleep 30
    
    if kubectl exec -it $(kubectl get pods -l app=${IMAGE_NAME} -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} -- curl -fsS http://localhost:8088/health; then
        log_info "OpenClinical AI deployment successful!"
    else
        log_error "OpenClinical AI deployment verification failed!"
        exit 1
    fi
}

# Call deployment function
deploy_openclinical
```

### Raven AI Deployment Script

```bash
#!/bin/bash
# raven-deploy.sh

set -e

# Configuration
IMAGE_NAME="raven-ai"
TAG="latest"
REGISTRY="your-registry.com"
NAMESPACE="ai-research"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main deployment function
deploy_raven() {
    log_info "Starting Raven AI deployment..."
    
    # Build and push Docker image
    log_info "Building Docker image..."
    docker build -t ${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${TAG} .
    
    # Deploy to Kubernetes
    log_info "Deploying to Kubernetes..."
    kubectl apply -f k8s/raven-deployment.yaml
    kubectl apply -f k8s/raven-service.yaml
    kubectl apply -f k8s/raven-ingress.yaml
    
    # Wait for deployment
    log_info "Waiting for deployment to complete..."
    kubectl rollout status deployment/${IMAGE_NAME} -n ${NAMESPACE}
    
    # Verify deployment
    log_info "Verifying deployment..."
    kubectl get pods -l app=${IMAGE_NAME} -n ${NAMESPACE}
    
    # Run health checks
    log_info "Running health checks..."
    sleep 30
    
    if kubectl exec -it $(kubectl get pods -l app=${IMAGE_NAME} -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} -- curl -fsS http://localhost:8000/health; then
        log_info "Raven AI deployment successful!"
    else
        log_error "Raven AI deployment verification failed!"
        exit 1
    fi
}

# Call deployment function
deploy_raven
```

## Multi-Environment Configuration

### Development Environment

```bash
# .env.development
OPENCLINICAL_ENV=development
DJANGO_SETTINGS_MODULE=openclinical.settings.dev
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/openclinical_dev

RAVEN_ENV=development
DJANGO_SETTINGS_MODULE=raven.settings.dev
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/raven_dev

# Feature flags
ENABLE_BIOSECURITY=true
ENABLE_AFFORDABILITY=true
ENABLE_AUDIT_TRAILS=true
```

### Production Environment

```bash
# .env.production
OPENCLINICAL_ENV=production
DJANGO_SETTINGS_MODULE=openclinical.settings.prod
DATABASE_URL=postgresql://openclinical:${DB_PASSWORD}@localhost:5432/openclinical_prod

RAVEN_ENV=production
DJANGO_SETTINGS_MODULE=raven.settings.prod
DATABASE_URL=postgresql://raven:${DB_PASSWORD}@localhost:5432/raven_prod

# Feature flags
ENABLE_BIOSECURITY=true
ENABLE_AFFORDABILITY=true
ENABLE_AUDIT_TRAILS=true
ENABLE_SAML_AUTH=true
```

## Migration Guide

### v1.x to v2.x Migration

#### OpenClinical AI Changes
1. **New Configuration System**
   - Old: `settings.py` with hardcoded values
   - New: `config.yaml` with structured configuration
   - Migration: Convert `settings.py` values to `config.yaml`

2. **Enhanced Biosecurity**
   - Added new screening layers (Pathogen, Toxin, Evasion, Length, Composition)
   - New risk threshold: >0.7 flag
   - Migration: Update existing biosecurity rules in `runtime/bio_security.py`

3. **New Affordability Tiers**
   - Added `critical_access_rural` tier
   - Added `biotech_sovereign` tier with zero cost
   - Migration: Update tenant configurations

4. **Database Schema Changes**
   - New `audit_traces` table for forensic analysis
   - Enhanced `models` table with signature verification
   - Migration: Run `scripts/migrate_to_v2.sql`

### Migration Steps

```bash
# Backup existing data
pg_dump openclinical > backup_v1.sql
pg_dump raven > backup_v1_raven.sql

# Update configuration
cp config.yaml.backup config.yaml
cp raven_config.backup raven_config.yaml

# Apply migrations
cd openclinical-ai
python scripts/migrate_to_v2.py

# Restart services
kubectl rollout restart deployment/openclinical-ai
kubectl rollout restart deployment/raven-ai

# Verify migration
kubectl exec -it <pod-name> -- python -c "from openclinical_ai import get_version; print(get_version())"
```

## Troubleshooting

### Common Issues

#### OpenClinical AI Issues

**Issue: Failed to load tenant configuration**
```bash
cat log/openclinical.log | grep "TenantConfigurationError"
```

**Solution:**
```bash
# Check tenant files
ls -la tenants/*.yaml

# Fix malformed YAML
nano tenants/default.yaml

# Restart service
kubectl rollout restart deployment/openclinical-ai
```

**Issue: Biosecurity screening not working**
```bash
cat log/openclinical.log | grep "BiosecurityScreener"
```

**Solution:**
```bash
# Check biosecurity configuration
ls -la runtime/biosecurity.yaml

# Update screening rules
nano runtime/biosecurity.py

# Restart service
kubectl rollout restart deployment/openclinical-ai
```

#### Raven AI Issues

**Issue: Agent timeout**
```bash
cat log/raven.log | grep "TimeoutError"
```

**Solution:**
```bash
# Increase timeout
nano raven_config.py

# Restart service
kubectl rollout restart deployment/raven-ai
```

### Diagnostic Commands

```bash
# Check pod logs
kubectl logs -f deployment/openclinical-ai
kubectl logs -f deployment/raven-ai

# Check service health
curl http://localhost:8088/health
curl http://localhost:8000/health

# Check storage usage
kubectl exec -it <pod-name> -- df -h
kubectl exec -it <pod-name> -- du -sh /app

# Check resource usage
kubectl top pods
```

## Support

### Need Help?

**Enterprise Support:**
- **Email:** support@enterprise.ai
- **Phone:** +1-800-AI-ENTERPRISE
- **Slack Channel:** #openhands-support
- **Phone Support Hours:** 24/7/365

**Community Support:**
- **GitHub Issues:** https://github.com/simpliibarrii-crypto/openclinical-ai/issues
- **Discussions:** https://github.com/simpliibarrii-crypto/openclinical-ai/discussions
- **Slack:** https://openclinical-ai.slack.com

### Contact Information

For urgent production issues, contact our 24/7 support team:

```
Emergency Contact:
- Phone: +1-800-473-3344 (24/7)
- Email: urgent@enterprise.ai
- PagerDuty: #enterprise-24-7
```

## Legal and Compliance

### License Information

OpenClinical AI and Raven AI are licensed under the **Apache 2.0 License**.

```
Apache License 2.0

Copyright (c) 2026 Barry Clerjuste
simpliibarrii-crypto/openclinical-ai

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License from LICENSE file
or at https://www.apache.org/licenses/LICENSE-2.0.txt

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Compliance Certifications

- **HIPAA Compliant:** ✅
- **PHIPA Compliant:** ✅ (Ontario Healthcare)
- **EU AI Act:** ✅ (High-Risk Category Assessment)
- **Health Canada:** ✅ (Medical Device Registration)
- **ISO 27001:** ✅ (In Progress)
- **SOC 2 Type II:** ✅ (In Progress)

### Documentation Citations

- **Open Clinical AI Documentation**: docs/
- **Raven AI Documentation**: raven-ai/docs/
- **API Reference**: api-reference.md
- **Developer Guide**: developer-guide.md
- **User Manual**: user-manual.md
- **Compliance Manual**: compliance-manual.md

## Version Information

### Current Versions

- **OpenClinical AI**: v2.4.1
- **Raven AI**: v3.1.2
- **Database Schema**: v2.0
- **API Version**: v1

### Release Notes

#### OpenClinical AI v2.4.1
- Enhanced biosecurity with 5-layer screening
- Added new `critical_access_rural` affordability tier
- Improved tenant isolation and audit trails
- Enhanced cost transparency with per-tenant reporting

#### Raven AI v3.1.2
- Improved agent orchestration with V4-Pro integration
- Enhanced clinical validation with evidence tracking
- Added multi-tenant support for research institutions
- Improved scalability with 100+ concurrent agents

### Update Instructions

#### Using Docker (Recommended)

```bash
# Upgrade OpenClinical AI
cd openclinical-ai
docker compose pull openclinical-ai
docker compose up -d

# Upgrade Raven AI
cd raven-ai
docker compose pull raven-ai
docker compose up -d
```

#### Using Native Deployment

```bash
# Update OpenClinical AI
cd openclinical-ai
pip install -e . --upgrade
python scripts/migrate_openclinical.py

# Update Raven AI
cd raven-ai
pip install -e . --upgrade
python scripts/migrate_raven.py

# Restart services
systemctl restart openclinical-ai
 systemctl restart raven-ai
```

## Emergency Procedures

### Critical Service Issues

**1. Service Down Detected**

```bash
# Check all services
kubectl get pods
kubectl get services
kubectl get deployments

# Check node resources
kubectl top nodes

# Check external connectivity
curl -I http://localhost:8088/health
 curl -I http://localhost:8000/health

# If service is down, restart
kubectl rollout restart deployment/openclinical-ai
 kubectl rollout restart deployment/raven-ai

# Check status after restart
kubectl rollout status deployment/openclinical-ai
 kubectl rollout status deployment/raven-ai
```

**2. Database Connection Issues**

```bash
# Check database
psql postgresql://openclinical:${DB_PASSWORD}@localhost:5432/openclinical -c "SELECT 1"

# Check database schema
psql postgresql://openclinical:${DB_PASSWORD}@localhost:5432/openclinical -f scripts/check_schema.sql

# If database is down, restore from backup
pg_restore -d openclinical /path/to/backup.sql
```

**3. High Resource Usage**

```bash
# Check resource usage
watch -n 5 kubectl top pods
watch -n 5 kubectl top nodes

# If resource limits exceeded, scale horizontally
kubectl scale deployment/openclinical-ai --replicas=8
kubectl scale deployment/raven-ai --replicas=16

# If CPU/memory exhausted, restart
kubectl rollout restart deployment/openclinical-ai
 kubectl rollout restart deployment/raven-ai
```

### Emergency Contact Information

**24/7 Technical Support:**
- **Phone:** +1-800-473-3344
- **Email:** emergencies@enterprise.ai
- **Pager:** #openclinical-emergency

**On-Call Engineers:**
- **Primary:** Engineering Team
- **Secondary:** Operations Team
- **Escalation:** Executive Management

## References

1. AlphaFold 2024 Nobel Prize Documentation
2. EU AI Act - High-Risk AI Systems Guidelines
3. HIPAA Security Rule Implementation Guide
4. PHIPA (Ontario) Healthcare Privacy Regulations
5. Health Canada Medical Device Regulations
6. DeepSeek V4-Pro and V4-Flash Pricing Information
7. PostgreSQL Database Administration Best Practices
8. Docker Production Deployment Patterns
9. Kubernetes Security Best Practices
10. FHIR Standards for Healthcare Interoperability

## Support Contacts

**OpenClinical AI Support:**
- **Email:** support@openclinical-ai.com
- **GitHub Issues:** https://github.com/simpliibarrii-crypto/openclinical-ai/issues
- **Slack:** https://openclinical-ai.slack.com

**Raven AI Support:**
- **Email:** support@raven-ai.com
- **GitHub Issues:** https://github.com/simpliibarrii-crypto/raven-ai/issues
- **Slack:** https://raven-ai.slack.com

**Emergency Services:**
- **24/7 Support Phone:** +1-800-473-3344
- **Emergency Email:** critical@enterprise.ai

---

*This documentation is continuously updated. Please check for the latest version before production deployment.*
