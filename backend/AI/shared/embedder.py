from sentence_transformers import SentenceTransformer

_embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list:
    return _embedder.encode(text).tolist()