import requests
import chromadb
import json
import time
import os
from dotenv import load_dotenv
from shared.embedder import get_embedding

load_dotenv()

OPENFDA_URL = "https://api.fda.gov/drug/label.json"

# Common drugs in rural India / primary care settings
# Add more based on your target use case
COMMON_DRUGS = [
    "metformin", "amlodipine", "atorvastatin", "paracetamol",
    "amoxicillin", "azithromycin", "ciprofloxacin", "omeprazole",
    "aspirin", "ibuprofen", "warfarin", "rifampicin",
    "isoniazid", "ethambutol", "pyrazinamide",   # TB drugs
    "hydroxychloroquine", "artemether",            # Malaria
    "insulin", "glibenclamide", "lisinopril"
]

def fetch_drug_label(drug_name: str) -> dict | None:
    """Fetch drug label including interactions from OpenFDA."""
    params = {
        "search": f"openfda.generic_name:{drug_name}",
        "limit": 1
    }
    try:
        response = requests.get(OPENFDA_URL, params=params, timeout=10)
        data = response.json()
        
        if "results" not in data or not data["results"]:
            return None
        
        result = data["results"][0]
        
        # Extract the relevant fields
        return {
            "drug_name": drug_name,
            "warnings": result.get("warnings", [""])[0][:1000] if result.get("warnings") else "",
            "drug_interactions": result.get("drug_interactions", [""])[0][:2000] if result.get("drug_interactions") else "",
            "contraindications": result.get("contraindications", [""])[0][:1000] if result.get("contraindications") else "",
            "indications": result.get("indications_and_usage", [""])[0][:500] if result.get("indications_and_usage") else ""
        }
    
    except Exception as e:
        print(f"  ❌ Error fetching {drug_name}: {e}")
        return None

def ingest_openfda(drugs: list = COMMON_DRUGS):
    """
    Full OpenFDA ingestion pipeline.
    Fetches drug labels and stores interaction data in ChromaDB.
    """
    chroma_client = chromadb.PersistentClient(path="./chroma_store")
    collection = chroma_client.get_or_create_collection("drug_interactions")
    
    total_stored = 0
    
    for drug in drugs:
        print(f"\n💊 Fetching data for: {drug}")
        
        label = fetch_drug_label(drug)
        if not label:
            print(f"  ⚠️ No data found for {drug}")
            continue
        
        # Build a rich text document for each drug
        doc_text = f"""
DRUG: {label['drug_name'].upper()}

INDICATIONS:
{label['indications']}

DRUG INTERACTIONS:
{label['drug_interactions']}

WARNINGS:
{label['warnings']}

CONTRAINDICATIONS:
{label['contraindications']}
        """.strip()
        
        if len(doc_text) < 50:
            continue
        
        chunk_id = f"fda_{drug.replace(' ', '_')}"
        
        # Skip if already exists
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            print(f"  ⏭️ Already indexed, skipping.")
            continue
        
        embedding = get_embedding(doc_text)
        collection.add(
            documents=[doc_text],
            embeddings=[embedding],
            ids=[chunk_id],
            metadatas=[{
                "source": "OpenFDA",
                "drug_name": drug
            }]
        )
        
        total_stored += 1
        print(f"  ✅ Stored {drug}")
        
        # OpenFDA rate limit: 240 requests/minute without API key
        time.sleep(0.3)
    
    print(f"\n🎉 OpenFDA ingestion complete. {total_stored} drug records stored.")

if __name__ == "__main__":
    ingest_openfda()