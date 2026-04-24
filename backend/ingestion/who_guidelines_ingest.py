# ingestion/who_guidelines_ingest.py  — SIMPLIFIED RELIABLE VERSION

import chromadb
import os
from pypdf import PdfReader
from dotenv import load_dotenv
from shared.embedder import get_embedding

load_dotenv()

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_local_pdfs(pdf_folder: str = "./knowledge_base"):
    """
    Reads all PDFs from knowledge_base/ folder and ingests them.
    Just drop any medical PDF in that folder and run this — it handles the rest.
    """
    chroma_client = chromadb.PersistentClient(path="./chroma_store")
    collection = chroma_client.get_or_create_collection("clinical_guidelines")
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("⚠️ No PDFs found in knowledge_base/ folder.")
        print("   Download WHO guidelines manually and place them there.")
        return
    
    total_chunks = 0
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"\n📋 Ingesting: {pdf_file}")
        
        try:
            reader = PdfReader(pdf_path)
            full_text = ""
            
            # Cap at 60 pages to avoid token/time issues
            for page in reader.pages[:60]:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            if len(full_text) < 100:
                print(f"  ⚠️ Could not extract text — possibly scanned/image PDF")
                continue
            
            chunks = chunk_text(full_text)
            print(f"  📄 {len(chunks)} chunks extracted")
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"who_{pdf_file[:30]}_{i}".replace(" ", "_")
                
                existing = collection.get(ids=[chunk_id])
                if existing["ids"]:
                    continue
                
                embedding = get_embedding(chunk)
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    ids=[chunk_id],
                    metadatas=[{
                        "source": "WHO Guidelines",
                        "filename": pdf_file,
                    }]
                )
                total_chunks += 1
        
        except Exception as e:
            print(f"  ❌ Error processing {pdf_file}: {e}")
            continue
    
    print(f"\n✅ WHO ingestion complete — {total_chunks} chunks stored.")

if __name__ == "__main__":
    ingest_local_pdfs()