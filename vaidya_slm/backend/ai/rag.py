"""
RAG (Retrieval-Augmented Generation) Module for Vaidya SLM
Uses ayurveda_rag_chunks for knowledge-enhanced responses
"""

import json
import os
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import re


class AyurvedicRAG:
    """Retrieval-Augmented Generation for Ayurvedic knowledge"""
    
    def __init__(self, chunks_file: str = None):
        self.chunks: List[Dict] = []
        if chunks_file:
            self.chunks_file = chunks_file
        else:
            # Try multiple possible locations
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            possible_files = [
                os.path.join(base_path, "ayurveda_rag_chunks (1).jsonl"),  # Priority 1
                os.path.join(base_path, "ayurveda_rag_chunks.jsonl"),      # Priority 2
            ]
            self.chunks_file = None
            for file_path in possible_files:
                if os.path.exists(file_path):
                    self.chunks_file = file_path
                    break
            if not self.chunks_file:
                self.chunks_file = possible_files[0]  # Use first as default if none exist
        self._load_chunks()
    
    def _load_chunks(self):
        """Load JSONL chunks into memory"""
        if not os.path.exists(self.chunks_file):
            print(f"WARNING: RAG chunks file not found at {self.chunks_file}")
            return
        
        try:
            with open(self.chunks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.chunks.append(json.loads(line))
            print(f"✓ RAG: Loaded {len(self.chunks)} Ayurvedic knowledge chunks")
        except Exception as e:
            print(f"ERROR loading RAG chunks: {str(e)}")
    
    def _similarity_score(self, query: str, text: str) -> float:
        """Calculate similarity between query and text using multiple methods"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Extract keywords from query
        keywords = set(re.findall(r'\b\w+\b', query_lower))
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Keyword matching (high weight)
        keyword_match = len(keywords & text_words) / (len(keywords) + 1)
        
        # Sequence matching (lower weight)
        seq_ratio = SequenceMatcher(None, query_lower, text_lower).ratio()
        
        # Combined score
        score = (keyword_match * 0.7) + (seq_ratio * 0.3)
        return score
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 3,
        threshold: float = 0.1
    ) -> List[Dict]:
        """
        Retrieve relevant Ayurvedic knowledge chunks
        
        Args:
            query: User symptom/disease query
            top_k: Number of top results to return
            threshold: Minimum similarity score
        
        Returns:
            List of relevant chunks with metadata
        """
        if not self.chunks:
            return []
        
        # Score all chunks
        scored_chunks = []
        for chunk in self.chunks:
            score = self._similarity_score(query, chunk.get('text', ''))
            if score >= threshold:
                scored_chunks.append({
                    **chunk,
                    'similarity_score': score
                })
        
        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_chunks[:top_k]
    
    def build_context(self, retrieved_chunks: List[Dict]) -> str:
        """Convert retrieved chunks into context string for LLM"""
        if not retrieved_chunks:
            return ""
        
        context_parts = ["## Relevant Ayurvedic Knowledge Base:\n"]
        for idx, chunk in enumerate(retrieved_chunks, 1):
            text = chunk.get('text', '')
            score = chunk.get('similarity_score', 0)
            context_parts.append(f"{idx}. {text} (Relevance: {score:.1%})")
        
        return "\n".join(context_parts) + "\n"
    
    def augment_query(self, user_query: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        """
        Augment user query with retrieved RAG context
        
        Returns:
            Tuple of (augmented_prompt, retrieved_chunks)
        """
        retrieved_chunks = self.retrieve(user_query, top_k=top_k)
        context = self.build_context(retrieved_chunks)
        
        augmented_prompt = f"""Use the following Ayurvedic knowledge base to inform your response:

{context}

Now answer the user's query with this knowledge in mind:
User Query: {user_query}"""
        
        return augmented_prompt, retrieved_chunks


# Global RAG instance
_rag_instance = None

def get_rag() -> AyurvedicRAG:
    """Get or create global RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = AyurvedicRAG()
    return _rag_instance
