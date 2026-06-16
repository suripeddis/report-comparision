import os
import time
from datetime import date
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_client = None


def _get_client():
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
                "Check your .env file."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
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
