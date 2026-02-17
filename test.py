import ingest_transcript
from ingest_transcript import read_transcript

#text = "Questions or comments on that one?"
#choices = text.split("or", 1)
#print(choices)
#if(len(choices) == 2): 
#   print("Binary")
#else: 
#    print("Multiple Choice") 
#print(len(choices))

read_transcript('Reports/transcript.txt')
