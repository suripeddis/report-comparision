import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pipelines.steps.ingest_transcript import read_transcript
from pipelines.steps.classifier import classify_transcript

st.set_page_config(page_title="AAC Prompt Classifier", layout="wide")
st.title("AAC Prompt Classifier")

file = st.file_uploader(label="Upload transcript", type="srt")
button = st.button(label="Analyze")

if button and file:
    with st.spinner("Reading transcript..."):
        transcript_text = read_transcript(file)

    with st.spinner("Classifying prompts..."):
        results = classify_transcript(transcript_text)

    df = pd.DataFrame(results)
    counts = df["type"].value_counts().to_dict()


    color_map = {
        "open_ended":           {"fill": "#AFA9EC", "text": "#26215C", "badge_bg": "#EEEDFE", "badge_text": "#3C3489", "label": "Open-ended"},
        "choice":               {"fill": "#ED93B1", "text": "#4B1528", "badge_bg": "#FBEAF0", "badge_text": "#72243E", "label": "Choice"},
        "clarification":        {"fill": "#FAC775", "text": "#412402", "badge_bg": "#FAEEDA", "badge_text": "#633806", "label": "Clarification"},
        "guided":               {"fill": "#5DCAA5", "text": "#04342C", "badge_bg": "#E1F5EE", "badge_text": "#085041", "label": "Guided"},
        "reinforcement":        {"fill": "#F0997B", "text": "#4A1B0C", "badge_bg": "#FAECE7", "badge_text": "#712B13", "label": "Reinforcement"},
    }

    max_count = max(counts.values()) if counts else 1

    bar_rows = ""
    for ptype, count in sorted(counts.items(), key=lambda x: -x[1]):
        c = color_map.get(ptype, {"fill": "#ccc", "text": "#333", "label": ptype})
        pct = (count / max_count) * 100
        bar_rows += f"""
        <div class="bar-row">
            <div class="bar-label">{c['label']}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%; background:{c['fill']}; color:{c['text']}">
                    {count}
                </div>
            </div>
        </div>
        """

    table_rows = ""
    for _, row in df.iterrows():
        ptype = row["type"]
        c = color_map.get(ptype, {"badge_bg": "#eee", "badge_text": "#333", "label": ptype})
        table_rows += f"""
        <tr>
            <td>{row['prompt_text']}</td>
            <td><span class="badge" style="background:{c['badge_bg']}; color:{c['badge_text']}">{c['label']}</span></td>
        </tr>
        """

    html = f"""
    <style>
        body {{ font-family: sans-serif; padding: 1rem; color: #1a1a1a; }}
        .stats {{ display: flex; gap: 12px; margin-bottom: 1.5rem; }}
        .stat {{ background: #f5f5f3; border-radius: 8px; padding: 12px 20px; flex: 1; text-align: center; }}
        .stat-num {{ font-size: 28px; font-weight: 500; }}
        .stat-lbl {{ font-size: 11px; color: #777; margin-top: 2px; }}
        .section-title {{ font-size: 15px; font-weight: 500; margin-bottom: 1rem; }}
        .bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
        .bar-label {{ width: 130px; font-size: 13px; color: #555; text-align: right; flex-shrink: 0; }}
        .bar-track {{ flex: 1; height: 30px; background: #f0f0ee; border-radius: 4px; overflow: hidden; }}
        .bar-fill {{ height: 100%; border-radius: 4px; display: flex; align-items: center; padding-left: 10px; font-size: 13px; font-weight: 500; transition: width 0.6s ease; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 1rem; }}
        th {{ text-align: left; padding: 8px 12px; font-size: 12px; color: #777; border-bottom: 1px solid #e5e5e3; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #f0f0ee; vertical-align: top; }}
        tr:last-child td {{ border-bottom: none; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 500; white-space: nowrap; }}
    </style>

    <div class="stats">
        <div class="stat"><div class="stat-num">{len(df)}</div><div class="stat-lbl">total prompts</div></div>
        <div class="stat"><div class="stat-num">{df['type'].nunique()}</div><div class="stat-lbl">categories</div></div>

    </div>

    <div class="section-title">Prompt distribution</div>
    {bar_rows}

    <div class="section-title" style="margin-top:2rem">Classified prompts</div>
    <table>
        <thead><tr><th>Prompt text</th><th>Type</th></tr></thead>
        <tbody>{table_rows}</tbody>
    </table>
    """

    components.html(html, height=200 + len(df) * 52 + len(counts) * 44, scrolling=True)