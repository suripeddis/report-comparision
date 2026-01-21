import streamlit as st 
from extractor import extract_teach_ask_spell_sequences

st.title("Prompt Extraction")
uploaded_file = st.file_uploader(
    "Upload a .docx report",
    type=["docx"],
    accept_multiple_files=False
)
button = st.button("Process")

if(button == True): 
    if(uploaded_file is None): 
        st.error("Upload a .docx file first")
    else:
        sequences = extract_teach_ask_spell_sequences(uploaded_file)
        st.success(f"Extracted {len(sequences)} sequences")
    for s in sequences:
        st.json(s)


