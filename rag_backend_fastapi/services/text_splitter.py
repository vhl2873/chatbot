"""Text Splitter - Chunk text into smaller pieces"""
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class TextSplitter:
    """Service for splitting text into chunks with overlap"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[Dict]:
        """Split text into chunks with overlap"""
        if not text or not text.strip():
            logger.warning("Empty text provided to split_text")
            return []
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence boundaries
            if end < text_length:
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end),
                    text.rfind('\n', start, end)
                )
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start': start,
                    'end': end
                })
            
            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

