"""
Memory Manager module.
Handles the persistence of failure memories to enable long-term learning 
for the autonomous debugger.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from app.core.logger import get_logger

logger = get_logger(__name__)

class FailureMemoryManager:
    """Manages long-term storage of RAG failure patterns."""
    
    def __init__(
        self,
        storage_path: str = "app/memory/data/failure_memory.json",
    ) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.storage_path = Path(storage_path)
        self.logger.info(f"Save convo at: {storage_path}")
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self,) -> None:
        """Creates the storage directory and file if they don't exist."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
            
    def save_failure(
        self,
        query: str,
        failure_claims: List[Dict[str, Any]],
        suggestions: List[str]
    ) -> None:
        """
        Persists a new failure pattern to the long-term memory.
        """
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                memories = json.load(f)
            
            new_memory = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "hallucinations": failure_claims,
                "recommended_fixes": suggestions,
            }
            
            memories.append(new_memory)
            
            memories = memories[-100:]
            
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2)
                
            self.logger.info(f"[MEMORY] Successfully saved failure pattern for query: {query[:30]}...")
        
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")
    
    def load_relevant_memories(self,) -> List[Dict[str, Any]]:
        """
        Retrieves past failures. 
        """
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                memories = json.load(f)
            return memories[-5:]
        
        except Exception as e:
            self.logger.error(f"Failed to load memories: {e}")
            
# Singletion instance
memory_manager = FailureMemoryManager()