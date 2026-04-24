import requests
import streamlit as st
from typing import Optional

BACKEND_URL = "http://localhost:8001"


def _headers() -> dict:
    """Return auth headers if token is in session state."""
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _handle(response: requests.Response) -> dict:
    """Raise a clean error or return JSON."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        detail = response.json().get("detail", str(e))
        raise RuntimeError(detail)


# ── Auth ──────────────────────────────────────────────────────────────────────

def login(email: str, password: str) -> dict:
    # Mocking login for frontend UI testing
    if email == "demo@pulmocare.ai" and password == "demo1234":
        return {
            "access_token": "mock-token-1234",
            "user_id": 1,
            "full_name": "Demo Doctor",
            "role": "doctor"
        }
    
    # Generic fallback mock
    return {
        "access_token": "mock-token-generic",
        "user_id": 99,
        "full_name": email.split("@")[0].title(),
        "role": "doctor"
    }


def register(full_name: str, email: str, password: str,
             role: str = "patient", phone: str = "",
             age: int = None, gender: str = "") -> dict:
    # Mocking register for frontend UI testing
    return {
        "message": "User registered successfully",
        "user_id": 2
    }


def get_me() -> dict:
    r = requests.get(f"{BACKEND_URL}/auth/me", headers=_headers())
    return _handle(r)


# ── Patients ──────────────────────────────────────────────────────────────────

def list_patients() -> list:
    r = requests.get(f"{BACKEND_URL}/patients/", headers=_headers())
    return _handle(r)


def get_patient(patient_id: int) -> dict:
    r = requests.get(f"{BACKEND_URL}/patients/{patient_id}", headers=_headers())
    return _handle(r)


# ── Sessions ──────────────────────────────────────────────────────────────────

def create_session(patient_id: int) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/sessions/",
        json={"patient_id": patient_id},
        headers=_headers()
    )
    return _handle(r)


def update_session(session_id: int, **kwargs) -> dict:
    r = requests.patch(
        f"{BACKEND_URL}/sessions/{session_id}",
        json={k: v for k, v in kwargs.items() if v is not None},
        headers=_headers()
    )
    return _handle(r)


def get_patient_sessions(patient_id: int) -> list:
    r = requests.get(
        f"{BACKEND_URL}/sessions/patient/{patient_id}",
        headers=_headers()
    )
    return _handle(r)


# ── AI — Scribe ───────────────────────────────────────────────────────────────

def ask_scribe(question: str) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/scribe/query",
        json={"question": question},
        headers=_headers()
    )
    return _handle(r)


def ingest_document(file_bytes: bytes, filename: str) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/scribe/ingest",
        files={"file": (filename, file_bytes, "application/pdf")},
        headers=_headers()
    )
    return _handle(r)


# ── AI — X-Ray ────────────────────────────────────────────────────────────────

def analyze_xray(file_bytes: bytes, filename: str) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/xray/analyze",
        files={"file": (filename, file_bytes, "image/jpeg")},
        headers=_headers()
    )
    return _handle(r)


# ── AI — Cough ────────────────────────────────────────────────────────────────

def analyze_cough(file_bytes: bytes, filename: str) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/cough/analyze",
        files={"file": (filename, file_bytes, "audio/wav")},
        headers=_headers()
    )
    return _handle(r)


# ── AI — Prescription ─────────────────────────────────────────────────────────

def parse_prescription(file_bytes: bytes, filename: str) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/prescription/parse",
        files={"file": (filename, file_bytes, "image/jpeg")},
        headers=_headers()
    )
    return _handle(r)


def check_interactions(medications: list) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/prescription/interactions",
        json={"medications": medications},
        headers=_headers()
    )
    return _handle(r)


# ── AI — Transcribe + SOAP ────────────────────────────────────────────────────

def transcribe(file_bytes: bytes, filename: str) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/report/transcribe",
        files={"file": (filename, file_bytes, "audio/mp3")},
        headers=_headers()
    )
    return _handle(r)


# ── AI — Unified Report ───────────────────────────────────────────────────────

def get_unified_report(
    xray_result: Optional[dict] = None,
    cough_result: Optional[dict] = None,
    scribe_context: Optional[str] = None
) -> dict:
    r = requests.post(
        f"{BACKEND_URL}/ai/report/unified",
        json={
            "xray_result":    xray_result,
            "cough_result":   cough_result,
            "scribe_context": scribe_context
        },
        headers=_headers()
    )
    return _handle(r)


# ── Records ───────────────────────────────────────────────────────────────────

def save_record(patient_id: int, record_type: str,
                content: str, notes: str = "") -> dict:
    r = requests.post(
        f"{BACKEND_URL}/records/",
        json={"patient_id": patient_id, "record_type": record_type,
              "content": content, "notes": notes},
        headers=_headers()
    )
    return _handle(r)


def get_records(patient_id: int) -> list:
    r = requests.get(
        f"{BACKEND_URL}/records/patient/{patient_id}",
        headers=_headers()
    )
    return _handle(r)
