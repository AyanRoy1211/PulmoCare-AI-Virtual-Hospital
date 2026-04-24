import chromadb
import os
from pypdf import PdfReader
from dotenv import load_dotenv
from shared.embedder import get_embedding

load_dotenv()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def ingest_pdf(pdf_path: str, collection_name: str = "medical_knowledge"):
    try:
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Ensure chroma_store directory exists
        os.makedirs("./chroma_store", exist_ok=True)
        
        chroma_client = chromadb.PersistentClient(path="./chroma_store")
        collection = chroma_client.get_or_create_collection(collection_name)
        
        # Extract text from PDF with error handling
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        if not full_text.strip():
            raise ValueError("No text extracted from PDF")
        
        # Chunk it
        chunks = chunk_text(full_text)
        filename = os.path.basename(pdf_path)
        
        # Embed and store with progress tracking
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            embedding = get_embedding(chunk)
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{filename}_chunk_{i}"],
                metadatas=[{"filename": filename, "chunk_index": i}]
            )
        
        print(f"✅ Ingested {len(chunks)} chunks from {filename}")
        
    except Exception as e:
        print(f"Error ingesting PDF: {e}")
        raise