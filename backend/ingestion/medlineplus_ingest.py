import requests
import chromadb
import time
import os
from dotenv import load_dotenv
from shared.embedder import get_embedding

load_dotenv()

# Comprehensive list of medical topics
MEDICAL_TOPICS = [
    # Infectious diseases (critical for rural India)
    "tuberculosis", "malaria", "dengue fever", "typhoid",
    "cholera", "hepatitis", "HIV AIDS", "pneumonia",
    
    # Chronic diseases
    "diabetes", "hypertension", "heart disease", "stroke",
    "chronic kidney disease", "asthma", "COPD",
    
    # Common conditions
    "anemia", "malnutrition", "diarrhea", "fever",
    "chest pain", "headache", "back pain", "arthritis",
    
    # Women and child health
    "pregnancy complications", "malnutrition children",
    "vaccination immunization", "maternal health",
    
    # Mental health
    "depression", "anxiety", "mental health"
]

MEDLINE_SEARCH_URL = "https://wsearch.nlm.nih.gov/ws/query"


def fetch_medlineplus(topic: str) -> list:
    """Fetch health topic summaries from MedlinePlus."""
    params = {
        "db": "healthTopics",
        "term": topic,
        "retmax": 5,
        "rettype": "brief"
    }
    try:
        response = requests.get(MEDLINE_SEARCH_URL, params=params, timeout=10)
        
        # Parse the XML-like response for content
        content = response.text
        documents = []
        
        # Extract content between <content> tags
        import re
        snippets = re.findall(r'<content[^>]*>(.*?)</content>', content, re.DOTALL)
        titles = re.findall(r'<title[^>]*>(.*?)</title>', content, re.DOTALL)
        
        for i, snippet in enumerate(snippets):
            # Clean HTML tags
            clean = re.sub(r'<[^>]+>', ' ', snippet).strip()
            clean = ' '.join(clean.split())  # Normalize whitespace
            
            if len(clean) > 100:
                title = titles[i] if i < len(titles) else topic
                documents.append({
                    "text": f"Topic: {title}\n\n{clean}",
                    "title": title,
                    "topic": topic
                })
        
        return documents
    
    except Exception as e:
        print(f"  ❌ Error fetching '{topic}': {e}")
        return []

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_medlineplus():
    chroma_client = chromadb.PersistentClient(path="./chroma_store")
    collection = chroma_client.get_or_create_collection("medical_conditions")
    
    total_chunks = 0
    
    for topic in MEDICAL_TOPICS:
        print(f"\n🏥 Fetching MedlinePlus data for: '{topic}'")
        documents = fetch_medlineplus(topic)
        
        if not documents:
            print(f"  ⚠️ No results for '{topic}'")
            continue
        
        for doc in documents:
            chunks = chunk_text(doc["text"])
            
            for j, chunk in enumerate(chunks):
                chunk_id = f"medline_{topic[:20]}_{j}".replace(" ", "_")
                
                existing = collection.get(ids=[chunk_id])
                if existing["ids"]:
                    continue
                
                embedding = get_embedding(chunk)
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    ids=[chunk_id],
                    metadatas=[{
                        "source": "MedlinePlus",
                        "topic": topic,
                        "title": doc["title"]
                    }]
                )
                total_chunks += 1
        
        time.sleep(0.3)
    
    print(f"\n✅ MedlinePlus ingestion complete — {total_chunks} chunks stored.")

if __name__ == "__main__":
    ingest_medlineplus()