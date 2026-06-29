"""openclinical-ai runtime — inference server.

Minimal viable runtime that:
- Loads signed models from the registry
- Runs inference (placeholder for MVP — pluggable model adapters)
- Logs every call to the audit gateway
- Respects consent via the consent engine
- Returns FHIR-compatible responses

Run with:
    uvicorn runtime.server:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path as PathLib
from pydantic import BaseModel, Field

from runtime.config import settings
from runtime.models import ModelRegistry, ModelSignatureError
from runtime.audit import AuditLogger
from runtime.consent import ConsentEngine, ConsentDenied

logger = logging.getLogger("openclinical.runtime")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


# -- request / response schemas ---------------------------------------------


class InferenceRequest(BaseModel):
    """Request to run inference on a model."""
    model_id: str = Field(..., description="ID of the model to run (e.g., 'psw-shift-handoff-v1')")
    patient_id: str = Field(..., description="FHIR Patient.id of the patient")
    inputs: dict[str, Any] = Field(..., description="Model-specific input payload")
    consent_token: str | None = Field(None, description="FHIR Consent reference token")


class InferenceResponse(BaseModel):
    """Response from an inference call."""
    inference_id: str
    model_id: str
    model_version: str
    patient_id: str
    outputs: dict[str, Any]
    audit_event_id: str
    timestamp: str
    latency_ms: int


class HealthResponse(BaseModel):
    """Runtime health."""
    status: str
    version: str
    models_loaded: int
    uptime_seconds: float


# -- application lifecycle ---------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize runtime state on startup, clean up on shutdown."""
    logger.info("openclinical-ai runtime starting — version %s", __import__("runtime").__version__)

    app.state.registry = ModelRegistry(registry_path=settings.registry_path)
    app.state.audit = AuditLogger(audit_path=settings.audit_path)
    app.state.consent = ConsentEngine(consent_path=settings.consent_path)
    app.state.started_at = time.time()

    # Load any pre-registered models
    loaded = await app.state.registry.load_all()
    logger.info("loaded %d models from registry", loaded)

    yield

    logger.info("openclinical-ai runtime shutting down")


app = FastAPI(
    title="openclinical-ai runtime",
    description="Sovereign inference runtime for biology AI and clinical AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- endpoints ---------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Runtime health check."""
    return HealthResponse(
        status="healthy",
        version=request.app.version,
        models_loaded=len(request.app.state.registry.loaded_models),
        uptime_seconds=time.time() - request.app.state.started_at,
    )


@app.get("/models")
async def list_models(request: Request) -> dict[str, Any]:
    """List all loaded models."""
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


@app.post("/v1/inference", response_model=InferenceResponse)
async def inference(req: InferenceRequest, request: Request) -> InferenceResponse:
    """Run inference on a model with consent + audit.

    This is the core endpoint. Every call:
    1. Verifies the model exists + is loaded in the registry
    2. Checks consent for the patient via the consent engine
    3. Runs inference
    4. Logs the inference to the audit gateway
    5. Returns the output with audit event ID
    """
    started = time.time()
    inference_id = str(uuid.uuid4())

    registry: ModelRegistry = request.app.state.registry
    audit: AuditLogger = request.app.state.audit
    consent: ConsentEngine = request.app.state.consent

    # 1. Resolve model
    model = registry.get(req.model_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {req.model_id} not found in registry",
        )

    # 2. Check consent
    try:
        await consent.check(req.patient_id, req.model_id, req.consent_token)
    except ConsentDenied as e:
        # Log the denied attempt — important for compliance
        await audit.log(
            event_type="consent-denied",
            inference_id=inference_id,
            patient_id=req.patient_id,
            model_id=req.model_id,
            model_version=model.version,
            reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Consent denied: {e}",
        )

    # 3. Run inference
    try:
        outputs = await model.run(req.inputs)
    except Exception as e:
        logger.exception("inference failed for model %s", req.model_id)
        await audit.log(
            event_type="inference-error",
            inference_id=inference_id,
            patient_id=req.patient_id,
            model_id=req.model_id,
            model_version=model.version,
            reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed",
        )

    # 4. Log to audit
    audit_event_id = await audit.log(
        event_type="inference",
        inference_id=inference_id,
        patient_id=req.patient_id,
        model_id=req.model_id,
        model_version=model.version,
        inputs=req.inputs,
        outputs=outputs,
        consent_token=req.consent_token,
    )

    latency_ms = int((time.time() - started) * 1000)

    return InferenceResponse(
        inference_id=inference_id,
        model_id=req.model_id,
        model_version=model.version,
        patient_id=req.patient_id,
        outputs=outputs,
        audit_event_id=audit_event_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        latency_ms=latency_ms,
    )


@app.get("/audit/events")
async def list_audit_events(
    request: Request,
    patient_id: str | None = None,
    model_id: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List audit events (FHIR AuditEvent compatible)."""
    audit: AuditLogger = request.app.state.audit
    events = await audit.query(
        patient_id=patient_id,
        model_id=model_id,
        limit=limit,
    )
    return {"events": events, "count": len(events)}


class ConsentGrantRequest(BaseModel):
    """Request to grant consent for a patient."""
    patient_id: str = Field(..., description="FHIR Patient.id of the patient")
    scope: list[str] = Field(["*"], description="Scope of consent (model IDs or ['*'])")
    granted_by: str = Field(..., description="Identity of the consent granter (e.g. PSW ID)")
    expires_at: str | None = Field(None, description="Optional ISO 8601 expiry timestamp")


class ConsentGrantResponse(BaseModel):
    """Response from a consent grant."""
    patient_id: str
    token: str
    scope: list[str]
    granted_by: str
    granted_at: str


@app.post("/v1/consent/grant", response_model=ConsentGrantResponse)
async def consent_grant(req: ConsentGrantRequest, request: Request) -> ConsentGrantResponse:
    """Grant consent for a patient.

    Used by the PSW voice UI to grant consent at the start of a shift.
    In production, consent would be captured via a formal consent workflow
    linked to the EHR consent module — this MVP endpoint is for demo +
    development use.
    """
    consent: ConsentEngine = request.app.state.consent
    token = await consent.grant_consent(
        patient_id=req.patient_id,
        scope=req.scope,
        granted_by=req.granted_by,
        expires_at=req.expires_at,
    )
    return ConsentGrantResponse(
        patient_id=req.patient_id,
        token=token,
        scope=req.scope,
        granted_by=req.granted_by,
        granted_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


class ConsentRevokeRequest(BaseModel):
    """Request to revoke consent for a patient."""
    patient_id: str
    revoked_by: str


@app.post("/v1/consent/revoke")
async def consent_revoke(req: ConsentRevokeRequest, request: Request) -> dict[str, str]:
    """Revoke consent for a patient."""
    consent: ConsentEngine = request.app.state.consent
    await consent.revoke_consent(req.patient_id, req.revoked_by)


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