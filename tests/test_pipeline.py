"""Unit tests for the AAC Prompt Classifier pipeline."""

import io
import pytest

from pipelines.steps.ingest_transcript import read_transcript
from pipelines.steps.metrics import count_prompt_types, get_max_counts, results_to_df


# ---------------------------------------------------------------------------
# ingest_transcript
# ---------------------------------------------------------------------------

SAMPLE_SRT = (
    "1\n"
    "00:00:01,000 --> 00:00:03,000\n"
    "Hello, what do you see?\n"
    "\n"
    "2\n"
    "00:00:04,000 --> 00:00:06,000\n"
    "Find the letter S.\n"
)


def _make_file(content: str):
    """Wrap a string as a file-like object the way Streamlit would."""
    return io.BytesIO(content.encode("utf-8"))


def test_read_transcript_strips_headers():
    result = read_transcript(_make_file(SAMPLE_SRT))
    assert "00:00:01" not in result
    assert "00:00:04" not in result


def test_read_transcript_keeps_speech():
    result = read_transcript(_make_file(SAMPLE_SRT))
    assert "Hello, what do you see?" in result
    assert "Find the letter S." in result


def test_read_transcript_empty_file():
    result = read_transcript(_make_file(""))
    assert result == ""


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------

SAMPLE_RESULTS = [
    {"timestamp": "00:00:01", "prompt_text": "What do you see?", "type": "open_ended"},
    {"timestamp": "00:00:05", "prompt_text": "Find the letter S.", "type": "guided"},
    {"timestamp": "00:00:10", "prompt_text": "Great job, keep going!", "type": "reinforcement"},
    {"timestamp": "00:00:15", "prompt_text": "Did you mean this one?", "type": "clarification"},
    {"timestamp": "00:00:20", "prompt_text": "Pencil or pen?", "type": "choice"},
    {"timestamp": "00:00:25", "prompt_text": "Look up here.", "type": "guided"},
]


def test_count_prompt_types_returns_dict():
    counts = count_prompt_types(SAMPLE_RESULTS)
    assert isinstance(counts, dict)


def test_count_prompt_types_values():
    counts = count_prompt_types(SAMPLE_RESULTS)
    assert counts["guided"] == 2
    assert counts["open_ended"] == 1


def test_get_max_counts():
    counts = {"guided": 2, "open_ended": 1, "reinforcement": 1}
    assert get_max_counts(counts) == 2


def test_get_max_counts_empty():
    assert get_max_counts({}) == 1


def test_results_to_df_shape():
    df = results_to_df(SAMPLE_RESULTS)
    assert len(df) == len(SAMPLE_RESULTS)
    assert "type" in df.columns
    assert "prompt_text" in df.columns


def test_results_to_df_empty():
    df = results_to_df([])
    assert len(df) == 0
