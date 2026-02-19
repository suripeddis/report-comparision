import streamlit as st
from pipelines.steps.extractor import extract_teach_ask_spell_sequences
from pipelines.steps.ingest_transcript import read_transcript
from pipelines.steps.ingest_transcript import is_prompt
from pipelines.steps.ingest_transcript import open_ai_send

st.title("Teach Ask Spell Analysis")

report_tab, transcript_tab = st.tabs(["Report Analysis", "Prompt Analysis"])

with report_tab:
    uploaded_file = st.file_uploader(
        "Upload a .docx report",
        type=["docx"],
        accept_multiple_files=False
    )
    button = st.button("Process")

    label_types = {
        "Open-ended": 0,
        "Recall": 0,
        "Sentence generation": 0,
        "Yes/No": 0,
        "Binary choice": 0,
        "Multiple choice": 0,
        "Invite speller questions": 0,
        "Other/Unclear": 0
    }

    spell_types = {
        "Single word": 0,
        "Full sentence": 0,
        "Reasoning/explanation": 0,
        "Opinion/preference": 0,
        "Question": 0,
        "Boundary/self-advocacy": 0,
        "Creative association (optional)": 0,
        "Other/Unclear": 0
    }

    if button:
        if uploaded_file is None:
            st.error("Upload a .docx file first")
        else:
            sequences = extract_teach_ask_spell_sequences(uploaded_file)
            st.success(f"Extracted {len(sequences)} sequences")
            overview_tab, details_tab = st.tabs(["Overview", "Details"])

            with overview_tab:
                st.header("Overview")
                for s in sequences:
                    if s["ask type"] in label_types:
                        label_types[s["ask type"]] += 1
                    if s["spell type"] in spell_types:
                        spell_types[s["spell type"]] += 1

                col1, col2, col3, col4 = st.columns(4, gap="large")
                col1.metric("Total Sequences", len(sequences))

                if len(sequences) > 0:
                    col2.metric("Top Ask %", f"{(max(label_types.values()) / len(sequences)) * 100:.2f}%")
                    col3.metric("Top Spell %", f"{(max(spell_types.values()) / len(sequences)) * 100:.2f}%")
                else:
                    col2.metric("Top Ask %", "0.00%")
                    col3.metric("Top Spell %", "0.00%")

                col4.metric("Unclear Asks", label_types["Other/Unclear"])

                st.title("Ask Type Distribution")
                st.bar_chart(label_types)
                st.title("Spell Type Distribution")
                st.bar_chart(spell_types)

            with details_tab:
                st.header("Details")
                st.dataframe(sequences)

with transcript_tab:
    file_uploaded = st.file_uploader(
        "Upload a .txt or .srt transcript",
        type=["txt", "srt"],
        accept_multiple_files=False
    )

    button2 = st.button("Analyze")

 
    s2c_count = 0
    rpm_count = 0
    unclear_method_count = 0

    
    prompt_type_counts = {
        "Guided": 0,
        "Open-ended": 0,
        "Clarification": 0,
        "Reinforcement": 0,
        "Choice-based": 0,
        "Other/Unclear": 0
    }

    prompt_candidates = 0
    classified_count = 0
    none_returned = 0

    if button2:
        if file_uploaded is None:
            st.error("Upload a .txt or .srt file first")
        else:
            cleaned_file = read_transcript(file_uploaded)

            for line in cleaned_file:
                if not is_prompt(line):
                    continue

                prompt_candidates += 1

                result = open_ai_send(line)
                if result is None:
                    none_returned += 1
                    continue

                classified_count += 1

                method = "Unclear"
                prompt_type = "Other/Unclear"

                parts = [p.strip() for p in result.split("|", 1)]
                if len(parts) == 2:
                    method, prompt_type = parts[0], parts[1]

                
                if method == "S2C":
                    s2c_count += 1
                elif method == "RPM":
                    rpm_count += 1
                else:
                    unclear_method_count += 1

                if prompt_type in prompt_type_counts:
                    prompt_type_counts[prompt_type] += 1
                else:
                    prompt_type_counts["Other/Unclear"] += 1

         
            col1, col2, col3 = st.columns(3, gap="large")
            col1.metric("Total S2C", s2c_count)
            col2.metric("Total RPM", rpm_count)
            col3.metric("Method Unclear", unclear_method_count)

            st.title("Prompt Type Distribution")
            st.bar_chart(prompt_type_counts)
