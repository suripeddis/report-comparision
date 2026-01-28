from docx import Document
import re
from classifier import classify_ask_type

def extract_teach_ask_spell_sequences(uploaded_file):

    document = Document(uploaded_file)
    inside_section = False
    current_sequence = None
    current_field = None 
    sequence_list = []

    for p in document.paragraphs:
        text = p.text.strip()
        if text == "Teach-Ask-Spell Sequences":
            inside_section = True
            continue  
        if(inside_section == True):
            if text.startswith("Sequence"):
                if(current_sequence is not None):
                    sequence_list.append(current_sequence)
                current_sequence = {
                    "sequence_label": text,
                    "teach": "",
                    "ask": "",
                    "spell": "",
                    "ask type": ""
                }
                current_field = None
            elif(text.startswith("Teach:") and current_sequence is not None):
                phrase = current_sequence["teach"] = text.split(":", 1)[1].strip()

            elif(text.startswith("Ask:") and current_sequence is not None):
                phrase = current_sequence["ask"] = text.split(":", 1)[1].strip()
                norm = phrase.strip().lstrip('"').lstrip("'").rstrip('"').rstrip("'")
                ask_type = classify_ask_type(norm)
                current_sequence["ask type"] = ask_type
            
            elif(text.startswith("Spell:") and current_sequence is not None):
                phrase = current_sequence["spell"] = text.split(":", 1)[1].strip()

    if(current_sequence is not None):
        sequence_list.append(current_sequence)

    return sequence_list