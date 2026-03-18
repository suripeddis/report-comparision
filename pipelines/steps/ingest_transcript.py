import re


# def read_transcript(file_uploaded):
#     document = file_uploaded.read()
#     document = document.decode("utf-8", errors="replace")

#     pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n"
#     cleaned_content = re.sub(pattern, "", document)

#     lines = cleaned_content.splitlines()
#     print("TOTAL LINES AFTER CLEAN:", len(lines))
#     return lines

def read_transcript(file_uploaded):
    document = file_uploaded.read().decode("utf-8", errors="replace")
    pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n"
    return re.sub(pattern, "", document)


