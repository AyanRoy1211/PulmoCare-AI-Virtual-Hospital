
from shared.llm_client import chat
import os
from dotenv import load_dotenv

load_dotenv()

ROUTER_PROMPT = """
Classify this medical query into exactly ONE of these categories.
Return ONLY the category name, nothing else.

CATEGORIES:
- patient_docs         (asks about uploaded report, prescription, or personal test results)
- drug_knowledge       (asks about medications, dosages, side effects, drug interactions)  
- research_evidence    (asks for research findings, studies, statistics, evidence)
- clinical_guidelines  (asks about treatment protocols, TB, malaria, WHO guidelines)
- medical_conditions   (asks about diseases, symptoms, diagnosis, general medicine)

QUERY: {query}

CATEGORY:"""

def route_query(query: str) -> str:
    prompt = ROUTER_PROMPT.format(query=query)
    
    # Accumulate streaming response for routing
    full_response = ""
    for chunk in chat(prompt):
        full_response += chunk
    
    if not full_response or not full_response.strip():
        return "medical_conditions"
    
    collection = full_response.strip().lower()
    
    # Validate response is a known collection
    valid = ["patient_docs", "drug_knowledge", "research_evidence", 
             "clinical_guidelines", "medical_conditions"]
    
    return collection if collection in valid else "medical_conditions"