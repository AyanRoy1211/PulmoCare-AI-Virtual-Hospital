from shared.llm_client import chat
import os
from dotenv import load_dotenv

load_dotenv()

SOAP_PROMPT = """
You are an expert medical scribe. Based on the following transcript of a doctor-patient 
consultation, generate a detailed, structured SOAP note.

TRANSCRIPT:
{transcript}

Generate the SOAP note in this exact format:

## SUBJECTIVE
(What the patient reports — symptoms, history, complaints, duration)

## OBJECTIVE
(Observable/measurable findings mentioned — vitals, physical exam findings if any)

## ASSESSMENT
(Likely diagnosis or differential diagnoses based on the conversation)

## PLAN
(Treatment plan, medications mentioned, tests ordered, follow-up instructions)

## FLAGS
(Any urgent concerns, red flag symptoms, or critical findings that need immediate attention)

Be concise but clinically complete. If information for a section is not present in the 
transcript, write 'Not discussed in consultation.'
"""

def generate_soap_note(transcript: str):
    """
    Takes consultation transcript.
    Yields SOAP note chunks for streaming.
    """
    prompt = SOAP_PROMPT.format(transcript=transcript)
    
    try:
        for chunk in chat(prompt):
            yield chunk
    except Exception as e:
        yield f"Unable to generate SOAP note at this time. Error: {str(e)}"