"""Embedding Service - Generate embeddings using HuggingFace"""
import logging
from typing import List

from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence transformers"""
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy load embedding model"""
        if cls._model is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}", exc_info=True)
                raise Exception(f"Failed to load embedding model: {str(e)}")
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()

    @classmethod
    def generate_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        model = cls.get_model()
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        return embeddings.tolist()

    @classmethod
    def get_embedding_dimension(cls) -> int:
        """Get embedding dimension"""
        return settings.EMBEDDING_DIMENSION

