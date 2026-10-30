import os
from typing import List, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI

class CareerRAGAssistant:
    def __init__(self, api_key: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set the OPENAI_API_KEY environment variable to use career chat.")
        self.encoder = SentenceTransformer(embedding_model)
        self.client = OpenAI(api_key=api_key)
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks: List[str] = []

    def build_knoweledge_base(self, resume_text: str, jd_text: str):
        """Split documents into overlapping chunks and index them in FAISS."""
        self.index.reset()
        self.chunks = []

        all_text = f"RESUME CONTEXT:\n{resume_text}\n\nJOB CONTEXT:\n{jd_text}"
        paragraphs = [p.strip() for p in all_text.split("\n\n") if len(p.strip()) > 30]

        if not paragraphs:
            return

        self.chunks = paragraphs
        embeddings = self.encoder.encode(self.chunks, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))

    def query(self, question: str, top_k: int = 3) -> str:
        """Retrives relevant chunks and generated a grounded response."""
        if self.index.ntotal == 0:
            return "Please upload a resume and provide a job description first."

        query_vector = self.encoder.encode([question], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        top_k = min(max(top_k, 1), self.index.ntotal)
        _, indices = self.index.search(query_vector.astype(np.float32), top_k)
        retrived_context = "\n---\n".join([self.chunks[i] for i in indices[0] if 0 <= i < len(self.chunks)])

        prompt = f"""
You are an expert career advisor assistant. Answere the users's question using ONLY the provided context.
If the answere is not present in the context, given general best-practices career advice while specifying the context was missing.

Context:
{retrived_context}

User Question:
{question}
"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
