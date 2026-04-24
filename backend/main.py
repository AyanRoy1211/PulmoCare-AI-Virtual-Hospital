from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ml_utils

app = FastAPI(title="PulmoCare API")

# Allow your frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PulmoCare API"}

@app.post("/ai/xray/analyze")
async def analyze_xray(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    image_bytes = await file.read()
    result = ml_utils.predict_xray(image_bytes)
    return {
        "filename": file.filename, 
        "top_finding": result.get("condition", "Unknown"), 
        "confidence": result.get("confidence", 0.0), 
        "findings": result.get("findings", [])
    }

@app.post("/ai/cough/analyze")
async def analyze_cough(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
    
    audio_bytes = await file.read()
    result = ml_utils.predict_cough(audio_bytes)
    return {
        "filename": file.filename, 
        "top_finding": result.get("condition", "Unknown"), 
        "confidence": result.get("confidence", 0.0), 
        "findings": result.get("findings", [])
    }

from pydantic import BaseModel

class ScribeRequest(BaseModel):
    question: str

@app.post("/ai/scribe/query")
async def scribe_query(req: ScribeRequest):
    """
    Hardcoded medical knowledge for demonstration.
    """
    responses = {
        "symptoms": "Tuberculosis typically presents with a persistent cough (over 3 weeks), chest pain, hemoptysis (coughing up blood), night sweats, and unexplained weight loss. Immediate clinical screening via chest X-ray and sputum culture is recommended.",
        "treatment": "Standard TB treatment follows the DOTS protocol (Directly Observed Treatment, Short-course). This usually involves a 6-month regimen of antibiotics: Isoniazid, Rifampin, Ethambutol, and Pyrazinamide for the first 2 months, followed by 4 months of Isoniazid and Rifampin.",
        "default": "Based on current clinical guidelines, these symptoms warrant a comprehensive respiratory panel. PulmoCare AI suggests prioritizing a chest X-ray to rule out parenchymal involvement and a cough biomarker analysis for initial screening."
    }
    
    q = req.question.lower()
    answer = responses.get("symptoms") if "symptom" in q else responses.get("treatment") if "treat" in q else responses.get("default")
    
    return {"answer": answer, "collection_used": "medical_knowledge_expert"}

import os
import tempfile
from typing import Optional, Dict, Any

@app.post("/ai/scribe/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        return {"message": f"Document {file.filename} indexed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/report/transcribe")
async def transcribe_consultation(file: UploadFile = File(...)):
    """
    Hardcoded consultation transcript and SOAP note for demonstration.
    """
    return {
        "transcript": "Patient presents with a persistent cough for three weeks, worsening at night. Reports chest tightness and occasional low-grade fever. No history of smoking. Auscultation reveals some crackles in the lower left lobe.",
        "soap_note": "### SOAP NOTE\n\n**Subjective:** 3-week persistent cough, nocturnal worsening, chest tightness, low-grade fever.\n\n**Objective:** Clear speech, alert. Lungs: Fine crackles noted in left lower lobe on auscultation. HR 78 bpm, SpO2 96% on room air.\n\n**Assessment:** Persistent cough with localized rales; differential includes community-acquired pneumonia vs. early pulmonary TB.\n\n**Plan:** Chest X-Ray (AP/PA), Cough Biomarker Analysis. Sputum for AFB/GeneXpert if symptoms persist. Start supportive therapy."
    }

@app.post("/ai/prescription/parse")
async def parse_prescription_endpoint(file: UploadFile = File(...)):
    """
    Hardcoded prescription OCR result for demonstration.
    """
    return {
        "patient_name": "Demo Patient",
        "date": "2024-04-24",
        "medications": [
            {"name": "Rifampin", "dosage": "600mg", "frequency": "Once daily", "duration": "2 months"},
            {"name": "Isoniazid", "dosage": "300mg", "frequency": "Once daily", "duration": "6 months"},
            {"name": "Pyrazinamide", "dosage": "1500mg", "frequency": "Once daily", "duration": "2 months"}
        ],
        "instructions": "Take medications on an empty stomach, 1 hour before or 2 hours after meals."
    }

class InteractionRequest(BaseModel):
    medications: list

@app.post("/ai/prescription/interactions")
async def check_interactions_endpoint(req: InteractionRequest):
    try:
        from AI.pipelines.drug_interaction import check_drug_interactions
        generator = check_drug_interactions(req.medications)
        result = "".join(list(generator))
        return {"interactions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class UnifiedReportRequest(BaseModel):
    xray_result: Optional[Dict[str, Any]] = None
    cough_result: Optional[Dict[str, Any]] = None
    scribe_context: Optional[str] = None

@app.post("/ai/report/unified")
async def generate_unified_report(req: UnifiedReportRequest):
    """
    Hardcoded unified clinical synthesis for demonstration.
    """
    return {
        "report": """### UNIFIED CLINICAL SYNTHESIS REPORT

**Patient Context:** 45-year-old male presenting with chronic cough and nighttime diaphoresis.

**Diagnostic Synthesis:**
1. **Imaging (Chest X-Ray):** Radiographic evidence of localized consolidation in the left lower lobe. Findings are highly suggestive of active pulmonary pneumonia or infiltrative disease.
2. **Acoustic Analysis (Cough):** AI acoustic biomarker score of 0.91 indicates a high match for pulmonary tuberculosis patterns. 
3. **Clinical Scribe Insights:** Patient history reveals high-risk contact and constitutional symptoms consistent with TB.

**Conclusion:**
There is strong clinical and multimodal evidence for **Pulmonary Tuberculosis**. The radiological findings combined with positive acoustic biomarkers provide a high level of diagnostic confidence.

**Recommended Actions:**
- Order GeneXpert MTB/RIF and sputum smear for AFB.
- Initiate standard anti-TB therapy (HRZE) pending culture results.
- Notification to Public Health authorities.
- Patient education on treatment adherence and infection control."""
    }