import chromadb
from shared.llm_client import chat
from shared.embedder import get_embedding
from dotenv import load_dotenv
from sentence_transformers import util
import torch

load_dotenv()

RAG_PROMPT = """
You are a professional AI medical scribe assistant.

Your job is to answer the user's question using ONLY the information
provided in the context below.

=====================
CONTEXT DOCUMENTS
=====================
{context}

=====================
USER QUESTION
=====================
{question}

=====================
INSTRUCTIONS
=====================

1. Only use the provided context.
2. Do NOT invent or assume medical information.
3. If the context does not contain enough information, say:
"I don't have enough information in the database to answer this."
4. Cite sources using [Source X].
5. Be concise and medically accurate.

=====================
ANSWER
=====================
"""

VERIFY_PROMPT = """
You are a medical AI safety reviewer.

Verify whether the ANSWER is fully supported by the CONTEXT.

CONTEXT:
{context}

ANSWER:
{answer}

Instructions:
- If every claim in the answer is supported by the context, respond with: SAFE
- If the answer contains unsupported medical information, respond with: UNSAFE

Respond with only SAFE or UNSAFE.
"""


def expand_query(question: str):

    prompt = f"""
Generate 3 alternative search queries to retrieve medical
information relevant to this question.

Question: {question}

Return one query per line.
"""

    try:
        response = ""
        for token in chat(prompt):
            response += token
    except:
        return [question]

    queries = [q.strip("- ").strip() for q in response.split("\n") if q.strip()]
    queries.append(question)

    return queries[:4]


def compress_context(question, chunks, sources, top_k=3):

    question_embedding = torch.tensor(get_embedding(question))
    chunk_embeddings = [torch.tensor(get_embedding(c)) for c in chunks]

    scores = [
        util.cos_sim(question_embedding, emb).item()
        for emb in chunk_embeddings
    ]

    ranked = sorted(
        zip(chunks, sources, scores),
        key=lambda x: x[2],
        reverse=True
    )

    top_chunks = ranked[:top_k]

    context_chunks = [c for c, _, _ in top_chunks]
    context_sources = [s for _, s, _ in top_chunks]

    return context_chunks, context_sources


def verify_answer(context, answer):

    prompt = VERIFY_PROMPT.format(
        context=context,
        answer=answer
    )

    response = ""

    for token in chat(prompt):
        response += token

    return "SAFE" in response.upper()


def query_knowledge_base(question: str, collection_name: str = "medical_knowledge"):

    chroma_client = chromadb.PersistentClient(path="./chroma_store")
    collection = chroma_client.get_or_create_collection(collection_name)

    queries = expand_query(question)

    all_chunks = []
    all_sources = []

    for q in queries:

        embedding = get_embedding(q)

        results = collection.query(
            query_embeddings=[embedding],
            n_results=3
        )

        docs = results.get("documents", [[]])
        docs = docs[0] if docs else []

        metas = results.get("metadatas", [[]])
        metas = metas[0] if metas else []

        all_chunks.extend(docs)
        all_sources.extend(metas)

    if not all_chunks:
        yield "I'm sorry, I don't have enough information in my medical database to answer that."
        return

    # remove duplicates
    unique_chunks = []
    unique_sources = []

    for chunk, src in zip(all_chunks, all_sources):
        if chunk not in unique_chunks:
            unique_chunks.append(chunk)
            unique_sources.append(src)

    context_chunks, sources = compress_context(
        question,
        unique_chunks,
        unique_sources,
        top_k=3
    )

    context = ""
    for i, (chunk, source) in enumerate(zip(context_chunks, sources)):

        context += f"""
[Source {i+1}]
Document: {source.get('filename','Unknown')}

{chunk}
"""

    prompt = RAG_PROMPT.format(
        context=context,
        question=question
    )

    generated_answer = ""

    try:
        for token in chat(prompt):
            generated_answer += token
    except Exception as e:
        yield f"Error generating response: {str(e)}"
        return

    # hallucination check
    is_safe = verify_answer(context, generated_answer)

    if not is_safe:
        yield "⚠️ The generated answer may contain unsupported medical information based on the current documents."
        yield "\nPlease consult a licensed physician for medical advice."
        return

    # stream final safe answer
    for char in generated_answer:
        yield char