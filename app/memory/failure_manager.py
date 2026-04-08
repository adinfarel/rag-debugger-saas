from app.memory.vector_store import VectorMemory
import uuid
from datetime import datetime
from app.core.logger import get_logger


class FailureMemoryManager:
    def __init__(self, collection_name="hallucinations_pattern"):
        self.logger = get_logger(self.__class__.__name__)
        self.db     = VectorMemory(collection_name=collection_name)
        self.logger.info(
            f"ChromaDB created with collection name: {collection_name}"
        )
    
    def save_failure(
        self,
        query,
        model_answer,
        critiques,
    ):
        """Save pattern hallucination at databases"""
        failed_claims = [c['claim'] for c in critiques if not c.get("is_supported")]
        
        if not failed_claims:
            return
        
        doc_id = str(uuid.uuid4())
        text_to_index = f"Query: {query} | Hallucinations: {'. '.join(failed_claims)}"
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],
            "status": "hallucination_detected",
        }
        
        self.db.add_memory(text=text_to_index, metadata=metadata, doc_id=doc_id)
        self.logger.info(f"[MEMORY] Add data at Vector Database successfully.")
    
    def get_relevant_failures(
        self,
        current_query,
    ):
        """Search whether used to ever seen similarity hallucination with new query now."""
        return self.db.search_similar(query_text=current_query)