import json
import streamlit as st
import streamlit.components.v1 as components
from datetime import date
from html import escape as he

from pipelines.steps.ingest_transcript import read_transcript
from pipelines.steps.classifier import classify_transcript
from pipelines.steps.database import save_session, get_student_sessions, get_session_by_file
from pipelines.steps.metrics import (
    count_prompt_types,
    count_methods,
    get_max_counts,
    results_to_df,
    compute_trend_data,
)

st.set_page_config(page_title="AAC Prompt Classifier", layout="wide")
st.title("AAC Prompt Classifier")
st.caption("Upload an SRT transcript to classify facilitator prompts by type.")

RPM_TYPE_MAP = {
    "open_ended":    {"fill": "#AFA9EC", "badge_bg": "#EEEDFE", "badge_text": "#3C3489", "label": "Open-ended"},
    "choice":        {"fill": "#ED93B1", "badge_bg": "#FBEAF0", "badge_text": "#72243E", "label": "Choice"},
    "clarification": {"fill": "#FAC775", "badge_bg": "#FAEEDA", "badge_text": "#633806", "label": "Clarification"},
    "guided":        {"fill": "#5DCAA5", "badge_bg": "#E1F5EE", "badge_text": "#085041", "label": "Guided"},
    "reinforcement": {"fill": "#F0997B", "badge_bg": "#FAECE7", "badge_text": "#712B13", "label": "Reinforcement"},
}

S2C_TYPE_MAP = {
    "initiation":   {"fill": "#A5B4FC", "badge_bg": "#E8ECFE", "badge_text": "#312E81", "label": "Initiation",   "desc": "Verbal cue to start movement."},
    "continuation": {"fill": "#9CC8F5", "badge_bg": "#E3F0FC", "badge_text": "#0E3A66", "label": "Continuation", "desc": "Verbal cue to continue movement."},
    "gesture":      {"fill": "#F4A3A3", "badge_bg": "#FBE5E5", "badge_text": "#7A1F1F", "label": "Gesture",      "desc": "Physical cue such as pointing or guiding."},
    "direction":    {"fill": "#FCD68A", "badge_bg": "#FEF1D6", "badge_text": "#7A4A0E", "label": "Direction",    "desc": "Verbal spatial cue like “top row.”"},
    "none":         {"fill": "#D1D5DB", "badge_bg": "#F3F4F6", "badge_text": "#374151", "label": "None",         "desc": "Independent selection without prompting."},
}

# Descriptions for the RPM legend rendered under Method Breakdown.
RPM_TYPE_DESCRIPTIONS = {
    "guided":        "Step-by-step prompts directing the speller to specific actions or spellings.",
    "open_ended":    "Prompts that allow for reflective, spontaneous responses.",
    "clarification": "Requests for the speller to explain or expand on prior responses.",
    "reinforcement": "Encouragement and praise that affirms effort or correctness.",
    "choice":        "Offering 2–3 options to focus attention or invite preference.",
}

# Union for visualizations that ignore method (donut, distribution bars, table badges).
# S2C wins on overlapping keys ("reinforcement") since it's the more specific styling here.
COLOR_MAP = {**RPM_TYPE_MAP, **S2C_TYPE_MAP}

METHOD_MAP = {
    "s2c": {"bg": "#EEF2FF", "text": "#3730A3", "label": "S2C"},
    "rpm": {"bg": "#E0F2FE", "text": "#0369A1", "label": "RPM"},
}

DIWAKAR_MAP = {
    "encouragement":          {"bg": "#FFF4E5", "text": "#7A4A00", "label": "Encouragement",          "desc": "Motivational or supportive language to keep the participant engaged."},
    "dictation":              {"bg": "#FDE7E9", "text": "#7A1521", "label": "Dictation",              "desc": "Directly telling or spelling the target response."},
    "instruction":            {"bg": "#E6F0FB", "text": "#0B3D7A", "label": "Instruction",            "desc": "Explicit guidance about what action to take."},
    "stm":                    {"bg": "#EDE9FE", "text": "#3B1F94", "label": "STM",                    "desc": "Short-term memory support to help the participant recall."},
    "question":               {"bg": "#E0F2FE", "text": "#0C4A6E", "label": "Question",               "desc": "Asks something to prompt thinking, recall, or response."},
    "hands":                  {"bg": "#FCE7F3", "text": "#831843", "label": "Hands",                  "desc": "Hand-based guidance or demonstration."},
    "directional":            {"bg": "#FEF3C7", "text": "#78350F", "label": "Directional",            "desc": "Cue that directs attention or movement toward a target."},
    "positive_reinforcement": {"bg": "#DCFCE7", "text": "#065F46", "label": "Positive reinforcement", "desc": "Praise or rewarding feedback after a correct response."},
    "gaze_cue":               {"bg": "#E0E7FF", "text": "#3730A3", "label": "Gaze cue",               "desc": "Eye gaze or visual attention cue to guide focus."},
    "physical":               {"bg": "#FEE2E2", "text": "#7F1D1D", "label": "Physical",               "desc": "Physical assistance beyond simple hand guidance."},
    "regulation":             {"bg": "#CFFAFE", "text": "#155E75", "label": "Regulation",             "desc": "Helps regulate emotions, attention, or behavior."},
    "focus":                  {"bg": "#F3E8FF", "text": "#581C87", "label": "Focus",                  "desc": "Regains or maintains attention on the task."},
}


def _humanize(key: str) -> str:
    """Turn a snake_case key into a 'Capitalized phrase' for fallback labels."""
    return (key or "").replace("_", " ").capitalize()


def render_report(results: list, file_name: str, trend_data_json: str = '{"sessions":[]}'):
    df = results_to_df(results)
    counts = count_prompt_types(results)
    methods = count_methods(results)
    total = len(df)

    # Pad with zero counts so every known type appears in the donut/bar chart.
    for k in list(RPM_TYPE_MAP.keys()) + list(S2C_TYPE_MAP.keys()):
        counts.setdefault(k, 0)

    s2c_count = methods.get("s2c", 0)
    rpm_count = methods.get("rpm", 0)
    s2c_pct   = round(s2c_count / total * 100) if total else 0
    rpm_pct   = round(rpm_count / total * 100) if total else 0

    chart_data = json.dumps({
        "counts":     counts,
        "methods":    methods,
        "total":      total,
        "colorMap":   {k: v["fill"]  for k, v in COLOR_MAP.items()},
        "typeLabels": {k: v["label"] for k, v in COLOR_MAP.items()},
        "sequence": [
            {
                "type":   r.get("type", ""),
                "method": r.get("method", ""),
                "text":   r.get("prompt_text", "")[:70],
            }
            for r in results
        ],
    }).replace("</script>", "<\\/script>")

    def _method_type_rows(method_key: str, type_map: dict) -> str:
        rows_html = ""
        for _, row in df.iterrows():
            if row.get("method", "") != method_key:
                continue
            ptype = row.get("type", "")
            t = type_map.get(ptype, {"badge_bg": "#eee", "badge_text": "#555", "label": _humanize(ptype)})
            rows_html += (
                f'<tr>'
                f'<td class="mt-type-cell"><span class="badge" '
                f'style="background:{t["badge_bg"]};color:{t["badge_text"]}">{t["label"]}</span></td>'
                f'<td class="mt-prompt-cell">{he(row.get("prompt_text", ""))}</td>'
                f'</tr>'
            )
        if not rows_html:
            rows_html = '<tr><td colspan="2" class="mt-empty">No prompts of this method in this session.</td></tr>'
        return rows_html

    s2c_table_rows = _method_type_rows("s2c", S2C_TYPE_MAP)
    rpm_table_rows = _method_type_rows("rpm", RPM_TYPE_MAP)

    def _count_block(title, css_class, items):
        """Render one method's per-type counts (only types that appeared)."""
        rows = "".join(
            f'<li class="mtc-item"><span class="mtc-name">{he(label)}</span>'
            f'<span class="mtc-val">{n}</span></li>'
            for label, n in items
        )
        if not rows:
            rows = '<li class="mtc-empty">None in this session.</li>'
        return (
            f'<div class="mtc-group">'
            f'<div class="mtc-head {css_class}">{he(title)}</div>'
            f'<ul class="mtc-list">{rows}</ul>'
            f'</div>'
        )

    # Per-type counts within each method (S2C / RPM by `type`, Diwakar by labels).
    s2c_items = [(v["label"], int(((df["method"] == "s2c") & (df["type"] == k)).sum()))
                 for k, v in S2C_TYPE_MAP.items()]
    rpm_items = [(v["label"], int(((df["method"] == "rpm") & (df["type"] == k)).sum()))
                 for k, v in RPM_TYPE_MAP.items()]

    diwakar_counts = {}
    for _, row in df.iterrows():
        raw = row.get("diwakar_labels", [])
        if isinstance(raw, str):
            raw = [raw]
        elif not isinstance(raw, list):
            raw = []
        for lbl in raw:
            diwakar_counts[lbl] = diwakar_counts.get(lbl, 0) + 1
    diwakar_items = [(v["label"], diwakar_counts.get(k, 0))
                     for k, v in DIWAKAR_MAP.items()]

    method_type_counts = (
        _count_block("S2C", "mtc-s2c", s2c_items)
        + _count_block("RPM", "mtc-rpm", rpm_items)
        + _count_block("Diwakar's Lab", "mtc-dwk", diwakar_items)
    )

    def _legend_html(items):
        out = ""
        for i, (label, desc) in enumerate(items, 1):
            out += (
                f'<li class="ml-item">'
                f'<span class="ml-num">{i}.</span>'
                f'<span class="ml-label">{he(label)}</span>'
                f'<span class="ml-desc">{he(desc)}</span>'
                f'</li>'
            )
        return out

    s2c_legend_items = [(v["label"], v["desc"]) for v in S2C_TYPE_MAP.values()]
    rpm_legend_items = [(v["label"], RPM_TYPE_DESCRIPTIONS.get(k, "")) for k, v in RPM_TYPE_MAP.items()]
    s2c_legend = _legend_html(s2c_legend_items)
    rpm_legend = _legend_html(rpm_legend_items)

    diwakar_rows = ""
    for _, row in df.iterrows():
        raw_labels = row.get("diwakar_labels", [])
        if isinstance(raw_labels, str):
            raw_labels = [raw_labels]
        elif not isinstance(raw_labels, list):
            raw_labels = []
        if not raw_labels:
            continue
        badges = ""
        for lbl in raw_labels:
            d = DIWAKAR_MAP.get(lbl, {"bg": "#f3f4f6", "text": "#374151", "label": _humanize(lbl)})
            badges += (
                f'<span class="badge dbadge" '
                f'style="background:{d["bg"]};color:{d["text"]}">{d["label"]}</span>'
            )
        diwakar_rows += (
            '<tr>'
            f'<td class="mt-type-cell diwakar-cell">{badges}</td>'
            f'<td class="mt-prompt-cell">{he(row.get("prompt_text", ""))}</td>'
            '</tr>'
        )
    if not diwakar_rows:
        diwakar_rows = '<tr><td colspan="2" class="mt-empty">No Diwakar-labeled prompts in this session.</td></tr>'

    with open("templates/report_template.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    html = (
        html_template
        .replace("{total_prompts}",    str(total))
        .replace("{total_categories}", str(df["type"].nunique()))
        .replace("{s2c_count}",        str(s2c_count))
        .replace("{rpm_count}",        str(rpm_count))
        .replace("{s2c_pct}",          str(s2c_pct))
        .replace("{rpm_pct}",          str(rpm_pct))
        .replace("{s2c_table_rows}",     s2c_table_rows)
        .replace("{rpm_table_rows}",     rpm_table_rows)
        .replace("{method_type_counts}", method_type_counts)
        .replace("{diwakar_table_rows}", diwakar_rows)
        .replace("{s2c_legend}",         s2c_legend)
        .replace("{rpm_legend}",         rpm_legend)
        .replace("{file_name}",        he(file_name))
        .replace("{report_date}",      date.today().strftime("%B %d, %Y"))
        .replace("{chart_data}",       chart_data)
        .replace("{trend_data}",       trend_data_json.replace("</script>", "<\\/script>"))
    )

    components.html(html, height=980 + len(df) * 58, scrolling=True)


# ── Session metadata inputs ──
col1, col2, col3 = st.columns(3)
with col1:
    student_id = st.text_input(
        "Student name",
        help="Used to track history and show the cross-session trend chart.",
    )
with col2:
    practitioner = st.text_input("Practitioner name")
with col3:
    topic = st.text_input(
        "Session topic",
        help="Short description shown in the trend chart labels.",
    )

file   = st.file_uploader(label="Upload transcript (.srt)", type="srt")
button = st.button(label="Analyze", type="primary", disabled=file is None)

if button and file:
    results = None

    # Use cached classification if this file was already analyzed for this student
    if student_id:
        try:
            cached = get_session_by_file(student_id, file.name)
            if cached:
                results = cached["classified_prompts"]
                st.info("Loaded from saved session — skipped GPT.")
        except Exception:
            pass

    if results is None:
        try:
            with st.spinner("Reading transcript..."):
                transcript_text = read_transcript(file)
            with st.spinner("Classifying prompts with GPT-4..."):
                results = classify_transcript(transcript_text)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

        try:
            with st.spinner("Saving session..."):
                save_session(
                    file.name,
                    results,
                    student_id=student_id or None,
                    practitioner=practitioner or None,
                    topic=topic or None,
                )
        except Exception as e:
            st.warning(f"Results could not be saved to the database: {e}")

    trend_data_json = '{"sessions":[]}'
    if student_id:
        try:
            prior = get_student_sessions(student_id, limit=6)
            if len(prior) >= 2:
                trend_data_json = json.dumps(compute_trend_data(prior))
        except Exception:
            pass

    render_report(results, file.name, trend_data_json)

# ── Previous sessions browser ──
st.divider()
st.subheader("Previous Sessions")

history_student = student_id or st.text_input("Enter student name to view history", key="history_lookup")

if history_student:
    if st.button("Load history"):
        try:
            sessions = get_student_sessions(history_student, limit=20)
            st.session_state["history_sessions"] = sessions
            st.session_state["history_student"]  = history_student
        except Exception as e:
            st.error(f"Could not load history: {e}")

    sessions = st.session_state.get("history_sessions", [])
    if sessions and st.session_state.get("history_student") == history_student:
        def session_label(s):
            d = s.get("session_date") or "Unknown date"
            t = s.get("topic") or s.get("file_name", "")
            return f"{d} — {t}"

        labels  = [session_label(s) for s in sessions]
        choice  = st.selectbox("Select a session", labels)
        selected = sessions[labels.index(choice)]

        if st.button("View report"):
            results = selected.get("classified_prompts", [])
            if not results:
                st.warning("No classified prompts found for this session.")
            else:
                trend_data_json = '{"sessions":[]}'
                try:
                    prior = get_student_sessions(history_student, limit=6)
                    if len(prior) >= 2:
                        trend_data_json = json.dumps(compute_trend_data(prior))
                except Exception:
                    pass
                render_report(results, selected.get("file_name", ""), trend_data_json)
    elif st.session_state.get("history_sessions") == []:
        st.info("No sessions found for this student.")
