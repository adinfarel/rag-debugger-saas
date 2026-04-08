import chromadb
from chromadb.utils import embedding_functions
import os
from pathlib import Path

class VectorMemory:
    def __init__(
        self,
        collection_name="failure_memory"
    ):
        self.path       = Path("db/chroma")
        if not self.path.parent.exists():
            print(f"[FALLBACK] Directory database not found. Fallback created: {self.path}")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            
        self.client     = chromadb.PersistentClient(path="./db/chroma")
        self.emb_fn     = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.emb_fn
        )
    
    def add_memory(
        self,
        text,
        metadata,
        doc_id,
    ):
        """Save hallucination text to Chroma DB"""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
    def search_similar(
        self,
        query_text,
        n_results=3,
    ):
        """Search same failure based on semantic"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        return results