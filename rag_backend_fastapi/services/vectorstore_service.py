"""Vectorstore Service - ChromaDB operations for ANN search"""
import logging
from typing import Dict, List

from config import settings

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not installed. Vector search will be disabled.")


class VectorstoreService:
    _client = None
    _collection = None

    @classmethod
    def initialize(cls):
        """Initialize ChromaDB client and collection"""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Skipping initialization.")
            return
        
        if cls._client is not None:
            logger.debug("ChromaDB already initialized")
            return
        
        try:
            settings.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
            cls._client = chromadb.PersistentClient(
                path=str(settings.CHROMA_DB_PATH),
                settings=Settings(anonymized_telemetry=False)
            )
            cls._collection = cls._client.get_or_create_collection(
                name="rag_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {str(e)}", exc_info=True)
            cls._client = None
            cls._collection = None

    @classmethod
    def get_collection(cls):
        """Get ChromaDB collection"""
        if not CHROMADB_AVAILABLE:
            return None
        if cls._collection is None:
            cls.initialize()
        return cls._collection

    @classmethod
    def add_chunks(cls, doc_id: str, chunks: List[Dict], embeddings: List[List[float]]):
        """Add chunks with embeddings to ChromaDB"""
        collection = cls.get_collection()
        if collection is None:
            logger.warning("ChromaDB not available. Skipping vector storage.")
            return
        
        if not chunks or not embeddings:
            logger.warning("Empty chunks or embeddings provided")
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        ids = []
        documents = []
        metadatas = []
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{idx}"
            ids.append(chunk_id)
            documents.append(chunk.get('text', ''))
            metadatas.append({
                'doc_id': doc_id,
                'index': idx,
                'firestore_id': chunk.get('firestore_id', '')
            })
        
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(chunks)} chunks to ChromaDB for document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {str(e)}", exc_info=True)
            raise

    @classmethod
    def search_similar(cls, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar chunks using ANN"""
        collection = cls.get_collection()
        if collection is None:
            logger.warning("ChromaDB not available. Returning empty results.")
            return []
        
        if not query_embedding:
            logger.warning("Empty query embedding provided")
            return []
        
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            similar_chunks = []
            if results.get('ids') and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    similar_chunks.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i] if results.get('documents') else '',
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    })
            
            logger.debug(f"Found {len(similar_chunks)} similar chunks")
            return similar_chunks
        except Exception as e:
            logger.error(f"ChromaDB search failed: {str(e)}", exc_info=True)
            return []

    @classmethod
    def delete_document_chunks(cls, doc_id: str):
        """Delete all chunks for a document from ChromaDB"""
        collection = cls.get_collection()
        if collection is None:
            return
        
        try:
            results = collection.get(where={'doc_id': doc_id})
            if results['ids']:
                collection.delete(ids=results['ids'])
        except Exception as e:
            print(f"⚠️ Warning: Failed to delete chunks from ChromaDB: {str(e)}")

    @classmethod
    def get_collection_stats(cls) -> Dict:
        """Get collection statistics"""
        collection = cls.get_collection()
        if collection is None:
            return {'total_chunks': 0, 'status': 'not_available'}
        try:
            count = collection.count()
            return {'total_chunks': count}
        except Exception as e:
            return {'total_chunks': 0, 'error': str(e)}

