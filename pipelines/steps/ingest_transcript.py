import re


def read_transcript(file_uploaded) -> str:
    """Parse an SRT file and return its plain-text content.

    Strips all SRT sequence numbers and timestamp lines, leaving only
    the spoken-word content.
    """
    document = file_uploaded.read().decode("utf-8", errors="replace")
    pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n"
    return re.sub(pattern, "", document)
