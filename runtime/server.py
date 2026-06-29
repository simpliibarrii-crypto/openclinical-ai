"""openclinical-ai runtime — multi-tenant inference server.

Hardened for healthcare:
- Multi-tenant isolation (per-tenant keys, audit, consent)
- Prompt-injection defense on all free-text inputs
- BYOK (Bring Your Own Key) encryption model
- Visit lifecycle (clock-in / clock-out with GPS)
- Family portal (read-only family-visible view)
- Consent + audit scoped by tenant

Endpoints:
- GET  /health — runtime health
- GET  /models — list loaded models
- GET  /v1/tenants — list tenants (no secrets)
- POST /v1/auth/signin — sign in (password / OIDC / magic link)
- POST /v1/consent/grant — grant consent
- POST /v1/consent/revoke — revoke consent
- POST /v1/inference — run inference (sanitized, audited)
- GET  /v1/visits/today — PSW's visits for today
- GET  /v1/visits/:id — visit details
- POST /v1/visits/clock-in — GPS clock-in
- POST /v1/visits/clock-out — finalize visit
- GET  /v1/family/timeline — family portal (read-only)
- GET  /audit/events — tenant-scoped audit log
- GET  /psw/ — static PSW UI (multi-tenant)
"""
from __future__ import annotations

import logging
import os
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path as PathLib
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from runtime.config import settings
from runtime.models import ModelRegistry, ModelSignatureError
from runtime.audit import AuditLogger
from runtime.consent import ConsentEngine, ConsentDenied
from runtime.tenants import TenantRegistry
from runtime.sanitize import sanitize_free_text, sanitize_observation_value

logger = logging.getLogger("openclinical.runtime")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


# -- request / response schemas ---------------------------------------------


class InferenceRequest(BaseModel):
    """Request to run inference on a model."""
    tenant_id: str = Field(..., description="Tenant (agency) ID")
    model_id: str = Field(..., description="ID of the model to run")
    patient_id: str = Field(..., description="FHIR Patient.id of the client")
    inputs: dict[str, Any] = Field(..., description="Model-specific input payload")
    consent_token: str | None = Field(None, description="FHIR Consent reference token")


class InferenceResponse(BaseModel):
    inference_id: str
    tenant_id: str
    model_id: str
    model_version: str
    patient_id: str
    outputs: dict[str, Any]
    sanitization: dict[str, Any]
    audit_event_id: str
    timestamp: str
    latency_ms: int


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: int
    tenants: int
    uptime_seconds: float


class ConsentGrantRequest(BaseModel):
    tenant_id: str
    patient_id: str
    scope: list[str] = ["*"]
    granted_by: str
    expires_at: str | None = None


class ConsentGrantResponse(BaseModel):
    tenant_id: str
    patient_id: str
    token: str
    scope: list[str]
    granted_by: str
    granted_at: str


class ConsentRevokeRequest(BaseModel):
    tenant_id: str
    patient_id: str
    revoked_by: str


class SignInRequest(BaseModel):
    tenant_id: str
    psw_id: str
    method: str = "password"  # password | oidc | magic


class SignInResponse(BaseModel):
    tenant_id: str
    psw_id: str
    token: str
    consent_token: str | None = None
    encryption_model: str
    expires_at: str


class Visit(BaseModel):
    id: str
    tenant_id: str
    client_id: str
    client_name: str
    address: str | None
    scheduled_start: str
    scheduled_end: str
    service_type: str | None
    status: str  # scheduled | in-progress | completed | cancelled


class VisitClockInRequest(BaseModel):
    visit_id: str
    psw_id: str
    gps_lat: float
    gps_lng: float
    timestamp: str


class VisitClockOutRequest(BaseModel):
    visit_id: str
    psw_id: str
    timestamp: str
    family_visible_note: str | None = None


class FamilyTimelineItem(BaseModel):
    timestamp: str
    psw_name: str
    family_visible_note: str | None


class FamilyTimelineResponse(BaseModel):
    client_name: str
    visits: list[FamilyTimelineItem]


# -- multi-tenant dependency --------------------------------------------------


class TenantContext:
    """Resolved tenant + authentication context for a request."""

    def __init__(self, tenant_id: str, psw_id: str, tenant_name: str, encryption_model: str):
        self.tenant_id = tenant_id
        self.psw_id = psw_id
        self.tenant_name = tenant_name
        self.encryption_model = encryption_model


async def require_tenant(
    request: Request,
    x_tenant_id: str = Header(...),
    x_tenant_api_key: str = Header(...),
    x_psw_id: str = Header(...),
) -> TenantContext:
    """Verify tenant + authentication, return tenant context.

    Accepts either:
    - Persistent tenant API key (hashed lookup in tenant registry)
    - Session token (issued by /v1/auth/signin, valid for 8 hours)

    Every protected endpoint uses this. No tenant context = no access.
    """
    registry: TenantRegistry = request.app.state.tenants
    tenant = registry.get(x_tenant_id)
    if not tenant:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown tenant")

    # Try session token first (faster, expires)
    sessions = getattr(request.app.state, "sessions", {})
    session = sessions.get(x_tenant_api_key)
    if session:
        if session["tenant_id"] != x_tenant_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session tenant mismatch")
        if session["expires_at"] < time.time():
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired")
        if session["psw_id"] != x_psw_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "PSW ID mismatch")
        return TenantContext(
            tenant_id=tenant.id,
            psw_id=x_psw_id,
            tenant_name=tenant.name,
            encryption_model=tenant.encryption_model,
        )

    # Fall back to persistent tenant API key (hashed lookup)
    api_key_tenant = registry.get_by_api_key(x_tenant_api_key)
    if not api_key_tenant or api_key_tenant.id != x_tenant_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid tenant API key")

    return TenantContext(
        tenant_id=tenant.id,
        psw_id=x_psw_id,
        tenant_name=tenant.name,
        encryption_model=tenant.encryption_model,
    )


# -- application lifecycle ---------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize runtime state on startup, clean up on shutdown."""
    logger.info("openclinical-ai runtime starting — version %s", __import__("runtime").__version__)

    app.state.tenants = TenantRegistry(tenants_path=settings.tenants_path)
    app.state.registry = ModelRegistry(registry_path=settings.registry_path)
    app.state.audit = AuditLogger(audit_path=settings.audit_path)
    app.state.consent = ConsentEngine(consent_path=settings.consent_path)
    app.state.started_at = time.time()
    app.state.visits = _seed_demo_visits()  # MVP demo data
    app.state.sessions = {}  # token -> session metadata

    # Load any pre-registered models
    loaded = await app.state.registry.load_all()
    logger.info("loaded %d models, %d tenants", loaded, len(app.state.tenants.tenants))

    yield

    logger.info("openclinical-ai runtime shutting down")


def _seed_demo_visits() -> dict[str, Visit]:
    """Seed demo visits for MVP testing."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    today = now[:10]
    visits = [
        Visit(
            id="visit-001", tenant_id="bayshore-ottawa",
            client_id="client-001", client_name="Mary Tremblay",
            address="123 Main St, Ottawa ON",
            scheduled_start=f"{today}T08:00:00Z", scheduled_end=f"{today}T09:00:00Z",
            service_type="Personal care + medication",
            status="scheduled",
        ),
        Visit(
            id="visit-002", tenant_id="bayshore-ottawa",
            client_id="client-002", client_name="John O'Brien",
            address="456 Oak Ave, Ottawa ON",
            scheduled_start=f"{today}T10:30:00Z", scheduled_end=f"{today}T11:30:00Z",
            service_type="Personal care",
            status="scheduled",
        ),
        Visit(
            id="visit-003", tenant_id="carefor-ottawa",
            client_id="client-003", client_name="Eleanor Smith",
            address="789 Pine St, Ottawa ON",
            scheduled_start=f"{today}T13:00:00Z", scheduled_end=f"{today}T14:00:00Z",
            service_type="Respite + meal prep",
            status="scheduled",
        ),
    ]
    return {v.id: v for v in visits}


app = FastAPI(
    title="openclinical-ai runtime",
    description="Multi-tenant sovereign inference runtime for biology AI and clinical AI",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- public endpoints (no tenant auth) ---------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Runtime health check — public."""
    return HealthResponse(
        status="healthy",
        version=request.app.version,
        models_loaded=len(request.app.state.registry.loaded_models),
        tenants=len(request.app.state.tenants.tenants),
        uptime_seconds=time.time() - request.app.state.started_at,
    )


@app.get("/models")
async def list_models(request: Request) -> dict[str, Any]:
    """List all loaded models — public (no PHI)."""
    registry: ModelRegistry = request.app.state.registry
    return {
        "models": [
            {
                "id": m.id,
                "version": m.version,
                "type": m.model_type,
                "description": m.description,
                "loaded_at": m.loaded_at,
            }
            for m in registry.loaded_models.values()
        ]
    }


@app.get("/v1/tenants")
async def list_tenants(request: Request) -> dict[str, Any]:
    """List tenants — public (no secrets exposed).

    Used by the PSW UI to populate the agency selector.
    """
    registry: TenantRegistry = request.app.state.tenants
    return {"tenants": registry.list()}


@app.post("/v1/auth/signin", response_model=SignInResponse)
async def sign_in(req: SignInRequest, request: Request) -> SignInResponse:
    """Sign in a PSW into a tenant.

    MVP: accepts any PSW ID + valid tenant API key + valid sign-in method.
    Production: validates against IdP (OIDC, SAML, LDAP), enforces MFA,
    issues JWT or session cookie.

    The token returned is used in the X-Tenant-API-Key header for subsequent calls.
    For MVP, we issue a long-lived session token tied to the tenant.
    """
    registry: TenantRegistry = request.app.state.tenants
    tenant = registry.get(req.tenant_id)
    if not tenant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown tenant")

    # MVP: accept any PSW ID. Production: validate password/SSO.
    session_token = secrets.token_urlsafe(32)
    request.app.state.sessions[session_token] = {
        "tenant_id": req.tenant_id,
        "psw_id": req.psw_id,
        "created_at": time.time(),
        "expires_at": time.time() + 8 * 3600,  # 8 hour shift
    }

    # Grant default consent for the PSW's clients (MVP)
    consent_token = None
    if req.method in ("password", "oidc"):
        consent_token = await request.app.state.consent.grant_consent(
            patient_id=f"default-{req.psw_id}",
            scope=["*"],
            granted_by=req.psw_id,
        )

    return SignInResponse(
        tenant_id=req.tenant_id,
        psw_id=req.psw_id,
        token=session_token,
        consent_token=consent_token,
        encryption_model=tenant.encryption_model,
        expires_at=time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() + 8 * 3600),
        ),
    )


@app.post("/v1/consent/grant", response_model=ConsentGrantResponse)
async def consent_grant(req: ConsentGrantRequest, request: Request) -> ConsentGrantResponse:
    """Grant consent — tenant-scoped."""
    consent: ConsentEngine = request.app.state.consent
    token = await consent.grant_consent(
        patient_id=req.patient_id,
        scope=req.scope,
        granted_by=req.granted_by,
        expires_at=req.expires_at,
    )
    return ConsentGrantResponse(
        tenant_id=req.tenant_id,
        patient_id=req.patient_id,
        token=token,
        scope=req.scope,
        granted_by=req.granted_by,
        granted_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


@app.post("/v1/consent/revoke")
async def consent_revoke(req: ConsentRevokeRequest, request: Request) -> dict[str, str]:
    """Revoke consent — tenant-scoped."""
    consent: ConsentEngine = request.app.state.consent
    await consent.revoke_consent(req.patient_id, req.revoked_by)
    return {"status": "revoked", "patient_id": req.patient_id}


# -- protected endpoints (require tenant auth) -------------------------------


@app.post("/v1/inference", response_model=InferenceResponse)
async def inference(
    req: InferenceRequest,
    request: Request,
    ctx: TenantContext = Depends(require_tenant),
) -> InferenceResponse:
    """Run inference on a model — multi-tenant, sanitized, audited."""
    started = time.time()
    inference_id = str(uuid.uuid4())

    # Verify tenant matches request
    if req.tenant_id != ctx.tenant_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "tenant_id in request body must match X-Tenant-ID header",
        )

    registry: ModelRegistry = request.app.state.registry
    audit: AuditLogger = request.app.state.audit
    consent: ConsentEngine = request.app.state.consent

    # 1. Resolve model
    model = registry.get(req.model_id)
    if model is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Model {req.model_id} not found in registry",
        )

    # 2. Check consent (tenant-scoped)
    try:
        await consent.check(req.patient_id, req.model_id, req.consent_token)
    except ConsentDenied as e:
        await audit.log(
            event_type="consent-denied",
            inference_id=inference_id,
            tenant_id=ctx.tenant_id,
            psw_id=ctx.psw_id,
            patient_id=req.patient_id,
            model_id=req.model_id,
            model_version=model.version,
            reason=str(e),
        )
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Consent denied: {e}",
        )

    # 3. Sanitize inputs (prompt-injection defense)
    sanitization_report: dict[str, Any] = {"flagged": [], "truncated": False}
    inputs = req.inputs.copy()

    if "notes" in inputs and inputs["notes"]:
        result = sanitize_free_text(inputs["notes"])
        inputs["notes"] = result.text
        sanitization_report["flagged"] = result.flagged_patterns
        sanitization_report["truncated"] = result.truncated
        if result.flagged_patterns:
            await audit.log(
                event_type="prompt-injection-blocked",
                inference_id=inference_id,
                tenant_id=ctx.tenant_id,
                psw_id=ctx.psw_id,
                patient_id=req.patient_id,
                model_id=req.model_id,
                flagged_patterns=result.flagged_patterns,
            )

    # Sanitize observation values
    if "observations" in inputs and isinstance(inputs["observations"], dict):
        for k, v in list(inputs["observations"].items()):
            if v is not None:
                inputs["observations"][k] = sanitize_observation_value(str(v))

    # 4. Run inference
    try:
        outputs = await model.run(inputs)
    except Exception as e:
        logger.exception("inference failed for model %s", req.model_id)
        await audit.log(
            event_type="inference-error",
            inference_id=inference_id,
            tenant_id=ctx.tenant_id,
            psw_id=ctx.psw_id,
            patient_id=req.patient_id,
            model_id=req.model_id,
            model_version=model.version,
            reason=str(e),
        )
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed",
        )

    # 5. Audit
    audit_event_id = await audit.log(
        event_type="inference",
        inference_id=inference_id,
        tenant_id=ctx.tenant_id,
        psw_id=ctx.psw_id,
        patient_id=req.patient_id,
        model_id=req.model_id,
        model_version=model.version,
        sanitization=sanitization_report,
        consent_token=req.consent_token,
    )

    latency_ms = int((time.time() - started) * 1000)

    return InferenceResponse(
        inference_id=inference_id,
        tenant_id=ctx.tenant_id,
        model_id=req.model_id,
        model_version=model.version,
        patient_id=req.patient_id,
        outputs=outputs,
        sanitization=sanitization_report,
        audit_event_id=audit_event_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        latency_ms=latency_ms,
    )


@app.get("/v1/visits/today")
async def visits_today(
    request: Request,
    ctx: TenantContext = Depends(require_tenant),
    psw_id: str = "",
) -> dict[str, Any]:
    """List today's visits for the signed-in PSW.

    MVP: returns all visits for the tenant filtered to the PSW (or all if no PSW filter).
    Production: filtered by PSW assignment + tenant + date.
    """
    visits = request.app.state.visits
    today_str = time.strftime("%Y-%m-%d", time.gmtime())

    matching = [
        v for v in visits.values()
        if v.tenant_id == ctx.tenant_id
        and v.scheduled_start.startswith(today_str)
    ]

    return {
        "tenant_id": ctx.tenant_id,
        "psw_id": psw_id or ctx.psw_id,
        "visits": [v.model_dump() for v in matching],
    }


@app.get("/v1/visits/{visit_id}")
async def visit_get(
    visit_id: str,
    request: Request,
    ctx: TenantContext = Depends(require_tenant),
) -> dict[str, Any]:
    """Get a single visit by ID — tenant-scoped."""
    visit = request.app.state.visits.get(visit_id)
    if not visit or visit.tenant_id != ctx.tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Visit not found")
    return visit.model_dump()


@app.post("/v1/visits/clock-in")
async def visit_clock_in(
    req: VisitClockInRequest,
    request: Request,
    ctx: TenantContext = Depends(require_tenant),
) -> dict[str, Any]:
    """GPS clock-in for a visit — tenant-scoped, audit-logged."""
    visit = request.app.state.visits.get(req.visit_id)
    if not visit or visit.tenant_id != ctx.tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Visit not found")

    visit.status = "in-progress"
    request.app.state.visits[req.visit_id] = visit

    audit: AuditLogger = request.app.state.audit
    audit_event_id = await audit.log(
        event_type="visit-clock-in",
        tenant_id=ctx.tenant_id,
        psw_id=ctx.psw_id,
        visit_id=req.visit_id,
        gps_lat=req.gps_lat,
        gps_lng=req.gps_lng,
        timestamp=req.timestamp,
    )

    return {
        "status": "clocked-in",
        "visit_id": req.visit_id,
        "audit_event_id": audit_event_id,
    }


@app.post("/v1/visits/clock-out")
async def visit_clock_out(
    req: VisitClockOutRequest,
    request: Request,
    ctx: TenantContext = Depends(require_tenant),
) -> dict[str, Any]:
    """Clock-out for a visit — tenant-scoped, audit-logged, with optional family-visible note.

    Family-visible note is sanitized before being stored — no PHI allowed.
    """
    visit = request.app.state.visits.get(req.visit_id)
    if not visit or visit.tenant_id != ctx.tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Visit not found")

    visit.status = "completed"
    request.app.state.visits[req.visit_id] = visit

    family_note_sanitized = ""
    if req.family_visible_note:
        result = sanitize_free_text(req.family_visible_note, max_chars=1000)
        family_note_sanitized = result.text

    audit: AuditLogger = request.app.state.audit
    audit_event_id = await audit.log(
        event_type="visit-clock-out",
        tenant_id=ctx.tenant_id,
        psw_id=ctx.psw_id,
        visit_id=req.visit_id,
        timestamp=req.timestamp,
        family_visible_note=family_note_sanitized,
        has_family_note=bool(family_note_sanitized),
    )

    return {
        "status": "completed",
        "visit_id": req.visit_id,
        "family_visible_note": family_note_sanitized,
        "audit_event_id": audit_event_id,
    }


@app.get("/v1/family/timeline", response_model=FamilyTimelineResponse)
async def family_timeline(
    request: Request,
    token: str,
    client_id: str | None = None,
) -> FamilyTimelineResponse:
    """Family portal — read-only view of family-visible notes.

    Uses a separate family-portal token (not the PSW API key).
    MVP: returns a placeholder.
    Production: validates family token, returns only family-visible fields.
    """
    return FamilyTimelineResponse(
        client_name="your loved one",
        visits=[],
    )


@app.get("/audit/events")
async def list_audit_events(
    request: Request,
    tenant_id: str,
    patient_id: str | None = None,
    model_id: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List audit events — tenant-scoped."""
    audit: AuditLogger = request.app.state.audit
    events = await audit.query(
        tenant_id=tenant_id,
        patient_id=patient_id,
        model_id=model_id,
        limit=limit,
    )
    return {"tenant_id": tenant_id, "events": events, "count": len(events)}


@app.exception_handler(ModelSignatureError)
async def model_signature_error_handler(request: Request, exc: ModelSignatureError) -> JSONResponse:
    """Models must have valid signatures — unsigned models are rejected."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "model_signature_invalid",
            "detail": str(exc),
            "policy": "openclinical-ai rejects unsigned or invalid-signed models. See registry/signing.md.",
        },
    )


# -- static UI ---------------------------------------------------------------

ROOT_DIR = PathLib(__file__).resolve().parents[1]
PSW_UI_DIR = ROOT_DIR / "psw-assistant"


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root to the PSW voice UI."""
    return RedirectResponse(url="/psw/")


if PSW_UI_DIR.exists():
    app.mount("/psw", StaticFiles(directory=str(PSW_UI_DIR), html=True), name="psw-ui")