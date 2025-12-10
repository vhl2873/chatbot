"""Prompt Service - Generate prompts for LLM"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PromptService:
    """Service for building prompts for LLM"""
    
    @staticmethod
    def build_rag_prompt(query: str, context_chunks: List[Dict]) -> str:
        """Build RAG prompt with context"""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not context_chunks:
            raise ValueError("Context chunks cannot be empty")
        
        # Build context text from chunks
        context_text = "\n\n".join([
            f"[Chunk {idx + 1}]: {chunk.get('text', '').strip()}"
            for idx, chunk in enumerate(context_chunks)
            if chunk.get('text', '').strip()
        ])
        
        if not context_text:
            raise ValueError("No valid context text found in chunks")
        
        prompt = f"""You are an AI assistant. Answer the question based ONLY on the provided context.

If the context does not contain enough information to answer the question, respond with: "Không đủ dữ liệu để trả lời câu hỏi này."

Context:
{context_text}

Question: {query}

Answer:"""
        
        logger.debug(f"Built RAG prompt with {len(context_chunks)} context chunks")
        return prompt

