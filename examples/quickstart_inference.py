"""
OpenClinical AI — Quickstart Inference Example

This script demonstrates how to:
1. Start the runtime server
2. Authenticate as a PSW (Personal Support Worker)
3. Submit a patient visit note for clinical inference
4. View the structured shift handoff output

Usage:
    python quickstart_inference.py

Prerequisites:
    pip install -e .. && pip install httpx
"""

import json
import subprocess
import sys
import time
import urllib.request

BASE_URL = "http://localhost:8000"
TENANT_ID = "bayshore-ottawa"
TENANT_API_KEY = "demo-api-key-bayshore-ottawa-2024"
PSW_ID = "psw-jdoe"


def wait_for_server(max_retries=10, delay=2):
    """Wait for the runtime server to become healthy."""
    for i in range(max_retries):
        try:
            req = urllib.request.Request(f"{BASE_URL}/health")
            resp = urllib.request.urlopen(req)
            if resp.status == 200:
                print(f"[OK] Server is healthy (attempt {i + 1})")
                return True
        except Exception:
            pass
        print(f"  Waiting for server... (attempt {i + 1}/{max_retries})")
        time.sleep(delay)
    return False


def sign_in():
    """Authenticate as a PSW and get a session token."""
    body = json.dumps({
        "tenant_id": TENANT_ID,
        "psw_id": PSW_ID,
        "method": "password",
    }).encode()

    req = urllib.request.Request(
        f"{BASE_URL}/v1/auth/signin",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": TENANT_ID,
            "X-Tenant-API-Key": TENANT_API_KEY,
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    print(f"[OK] Signed in as {PSW_ID} — token: {data['token'][:16]}...")
    return data["token"]


def run_inference(session_token):
    """Submit a patient visit note for clinical inference."""
    body = json.dumps({
        "tenant_id": TENANT_ID,
        "model_id": "psw-shift-handoff",
        "patient_id": "client-001",
        "inputs": {
            "notes": (
                "Mrs. Tremblay was alert and calm this morning. "
                "BP 128/82, HR 72, temp 36.8C, SpO2 97%. "
                "She walked to the bathroom with assistance and ate 75% of breakfast. "
                "Daughter called to check in at 10am."
            ),
            "observations": {
                "bp": "128/82",
                "hr": 72,
                "temp_c": 36.8,
                "spo2": 97,
                "meal_pct": 75,
                "mood": "alert and calm",
                "ambulation": "assisted",
            },
            "psw_id": PSW_ID,
            "resident_id": "client-001",
        },
    }).encode()

    req = urllib.request.Request(
        f"{BASE_URL}/v1/inference",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": TENANT_ID,
            "X-Tenant-API-Key": session_token,
            "X-PSW-ID": PSW_ID,
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    return data


def main():
    print("=" * 60)
    print("OpenClinical AI — Quickstart Inference")
    print("=" * 60)

    if not wait_for_server():
        print("\n[!] Server not available.")
        print("    Start it with: uvicorn runtime.server:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    session_token = sign_in()
    result = run_inference(session_token)

    print("\n--- Inference Result ---")
    print(f"Inference ID:  {result['inference_id']}")
    print(f"Model:         {result['model_id']} v{result['model_version']}")
    print(f"Patient:       {result['patient_id']}")
    print(f"Latency:       {result['latency_ms']}ms")
    print(f"Audit Event:   {result['audit_event_id']}")

    shift = result["outputs"]["shift_handoff"]
    print(f"\n--- Shift Handoff Summary ---")
    print(shift["summary"])

    if shift.get("concerns"):
        print(f"\n--- Concerns ({len(shift['concerns'])}) ---")
        for c in shift["concerns"]:
            print(f"  [{c['severity'].upper()}] {c['detail']}")

    print(f"\nFollow-up required: {'YES' if shift.get('followup_required') else 'No'}")
    print(f"\n[OK] Inference completed successfully.")


if __name__ == "__main__":
    main()
