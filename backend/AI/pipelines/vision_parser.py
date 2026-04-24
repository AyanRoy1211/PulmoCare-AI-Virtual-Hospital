import json
import os
import base64
from dotenv import load_dotenv
from shared.llm_client import vision

load_dotenv()

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode('utf-8')

EXTRACTION_PROMPT = """
You are a medical prescription parser. Extract ALL information from this prescription image.
Return ONLY a valid JSON object with this exact structure:
{
  "patient_name": "",
  "patient_age": "",
  "date": "",
  "doctor_name": "",
  "medications": [
    {
      "drug_name": "",
      "dosage": "",
      "frequency": "",
      "duration": "",
      "route": ""
    }
  ],
  "diagnosis": "",
  "instructions": "",
  "follow_up": ""
}
If any field is unclear or missing, use null. Return JSON only, no other text.
"""

def parse_prescription(image_path: str) -> dict:
    """
    Takes prescription image path.
    Returns structured JSON of all prescription details.
    """
    image_base64 = encode_image(image_path)

    raw = vision(EXTRACTION_PROMPT, image_base64)

    if not raw:
        return {"error": "No content returned from model"}

    clean = raw.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON. Raw output: {raw}")
        return {"error": "Invalid JSON format"}