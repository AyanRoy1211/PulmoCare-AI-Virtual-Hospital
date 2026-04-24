import requests
import chromadb
import time
import os
from dotenv import load_dotenv
from shared.embedder import get_embedding

load_dotenv()

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Medical topics relevant to rural India disease burden
# Expand this list as needed
TOPICS = [
    "tuberculosis diagnosis treatment",
    "pneumonia symptoms treatment",
    "diabetes type 2 management",
    "hypertension rural",
    "malaria diagnosis",
    "anemia children",
    "dengue fever symptoms",
    "typhoid fever treatment",
    "chest pain differential diagnosis",
    "drug interactions common medications"
]


def fetch_pubmed_ids(topic: str, max_results: int = 20) -> list:
    """Search PubMed and return list of PMIDs."""
    params = {
        "db": "pubmed",
        "term": topic,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance"
    }
    response = requests.get(PUBMED_SEARCH_URL, params=params)
    data = response.json()
    return data["esearchresult"]["idlist"]

def fetch_abstracts(pmids: list) -> list:
    """Fetch abstract text for a list of PMIDs."""
    ids_str = ",".join(pmids)
    params = {
        "db": "pubmed",
        "id": ids_str,
        "rettype": "abstract",
        "retmode": "text"
    }
    response = requests.get(PUBMED_FETCH_URL, params=params)
    
    # Split into individual abstracts
    raw = response.text
    abstracts = []
    
    for block in raw.split("\n\n\n"):
        block = block.strip()
        if len(block) > 100:  # Filter out noise
            abstracts.append(block)
    
    return abstracts

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_pubmed(topics: list = TOPICS, abstracts_per_topic: int = 20):
    """
    Full PubMed ingestion pipeline.
    Fetches abstracts for each topic and stores in ChromaDB.
    """
    chroma_client = chromadb.PersistentClient(path="./chroma_store")
    collection = chroma_client.get_or_create_collection("medical_knowledge")
    
    total_chunks = 0
    
    for topic in topics:
        print(f"\n📚 Fetching abstracts for: '{topic}'")
        
        try:
            pmids = fetch_pubmed_ids(topic, max_results=abstracts_per_topic)
            if not pmids:
                print(f"  ⚠️ No results found for '{topic}'")
                continue
            
            abstracts = fetch_abstracts(pmids)
            print(f"  ✅ Retrieved {len(abstracts)} abstracts")
            
            for i, abstract in enumerate(abstracts):
                chunks = chunk_text(abstract)
                
                for j, chunk in enumerate(chunks):
                    chunk_id = f"pubmed_{topic[:20]}_{i}_{j}".replace(" ", "_")
                    
                    # Skip if already exists
                    existing = collection.get(ids=[chunk_id])
                    if existing["ids"]:
                        continue
                    
                    embedding = get_embedding(chunk)
                    collection.add(
                        documents=[chunk],
                        embeddings=[embedding],
                        ids=[chunk_id],
                        metadatas=[{
                            "source": "PubMed",
                            "topic": topic,
                            "pmid_index": i
                        }]
                    )
                    total_chunks += 1
                
                # Respect PubMed rate limit — max 3 requests/second without API key
                time.sleep(0.4)
        
        except Exception as e:
            print(f"  ❌ Error on topic '{topic}': {e}")
            continue
    
    print(f"\n🎉 PubMed ingestion complete. {total_chunks} chunks stored.")

if __name__ == "__main__":
    ingest_pubmed()