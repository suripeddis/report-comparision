import os
import time
from datetime import date
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_secret(name: str):
    """Read a config value from the environment, falling back to Streamlit secrets.

    Locally these come from .env (via load_dotenv); on Streamlit Cloud they come
    from the app's Secrets (st.secrets), which aren't always exposed as plain
    environment variables.
    """
    val = os.getenv(name)
    if val:
        return val
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return None


def _get_client():
    global _client
    if _client is None:
        url = _get_secret("SUPABASE_URL")
        key = _get_secret("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set. Locally, check your "
                ".env file; on Streamlit Cloud, set them in the app's Secrets."
            )
        _client = create_client(url, key)
    return _client


def _retry(fn, retries=3, delay=1.0):
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
    raise last_err


def save_session(
    file_name: str,
    results: list,
    student_id: str = None,
    practitioner: str = None,
    topic: str = None,
) -> None:
    """Insert a classified session into the sessions table.

    Required Supabase schema additions beyond the base 'sessions' table:
        student_id   text
        practitioner text
        topic        text
        session_date date
    """
    payload = {
        "file_name": file_name,
        "classified_prompts": results,
        "session_date": date.today().isoformat(),
    }
    if student_id:
        payload["student_id"] = student_id
    if practitioner:
        payload["practitioner"] = practitioner
    if topic:
        payload["topic"] = topic
    _retry(lambda: _get_client().table("sessions").insert(payload).execute())


def get_session_by_file(student_id: str, file_name: str) -> dict | None:
    """Return an existing session for a student+file combo, or None if not found."""
    response = _retry(lambda: (
        _get_client()
        .table("sessions")
        .select("*")
        .eq("student_id", student_id)
        .eq("file_name", file_name)
        .limit(1)
        .execute()
    ))
    data = response.data
    return data[0] if data else None


def get_prior_session(student_id: str) -> dict | None:
    """Return the most recent session for a given student, or None."""
    response = _retry(lambda: (
        _get_client()
        .table("sessions")
        .select("*")
        .eq("student_id", student_id)
        .order("session_date", desc=True)
        .limit(1)
        .execute()
    ))
    data = response.data
    return data[0] if data else None


def get_student_sessions(student_id: str, limit: int = 6) -> list:
    """Return the most recent sessions for a student, returned oldest-first."""
    response = _retry(lambda: (
        _get_client()
        .table("sessions")
        .select("*")
        .eq("student_id", student_id)
        .order("session_date", desc=True)
        .limit(limit)
        .execute()
    ))
    return list(reversed(response.data))


def load_sessions() -> list:
    """Return all sessions."""
    response = _retry(lambda: _get_client().table("sessions").select("*").execute())
    return response.data
