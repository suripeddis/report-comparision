import pandas as pd

RPM_TYPES = ["open_ended", "choice", "clarification", "guided", "reinforcement"]
S2C_TYPES = [
    "initiation",
    "continuation",
    "gesture",
    "direction",
    "none",
]
ALL_TYPES = list(dict.fromkeys(RPM_TYPES + S2C_TYPES))


def count_prompt_types(results):
    df = pd.DataFrame(results)
    return df["type"].value_counts().to_dict()


def count_methods(results):
    df = pd.DataFrame(results)
    return df["method"].value_counts().to_dict() if "method" in df.columns else {}


def get_max_counts(counts):
    return max(counts.values()) if counts else 1


def results_to_df(results):
    return pd.DataFrame(results)


def compute_trend_data(sessions: list) -> dict:
    """Build per-session prompt-type distributions for the cross-session trend chart.

    Returns a dict with a 'sessions' list, each entry containing:
      label  — ISO date string (YYYY-MM-DD)
      topic  — session topic or file name
      total  — total prompt count
      counts — {type: count, ...}
      pcts   — {type: integer_percentage, ...}
    """
    rows = []
    for s in sessions:
        results = s.get("classified_prompts", [])
        if not results:
            continue
        df = pd.DataFrame(results)
        total = len(df)
        raw_counts = df["type"].value_counts().to_dict()
        rows.append({
            "label": (s.get("session_date") or "")[:10],
            "topic": s.get("topic") or s.get("file_name", ""),
            "total": total,
            "counts": {t: raw_counts.get(t, 0) for t in ALL_TYPES},
            "pcts": {
                t: round(raw_counts.get(t, 0) / total * 100) if total else 0
                for t in ALL_TYPES
            },
        })
    return {"sessions": rows}
