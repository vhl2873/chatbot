"""RAG Service - Main RAG pipeline orchestration"""
import logging
from typing import Dict

import google.generativeai as genai

from config import settings
from .embedding_service import EmbeddingService
from .firebase_service import FirebaseService
from .prompt_service import PromptService
from .text_splitter import TextSplitter
from .vectorstore_service import VectorstoreService

logger = logging.getLogger(__name__)


class RAGService:
    
    @staticmethod
    def process_document(file_content: str, doc_id: str, metadata: Dict):
        """Process uploaded document: chunk, embed, store"""
        try:
            logger.info(f"Processing document {doc_id}...")
            
            # Split text into chunks
            splitter = TextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            chunks = splitter.split_text(file_content)
            
            if not chunks:
                raise ValueError("No chunks generated from document")
            
            logger.info(f"Generated {len(chunks)} chunks for document {doc_id}")
            
            # Generate embeddings
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = EmbeddingService.generate_embeddings_batch(chunk_texts)
            
            # Save chunks with vectors to Firestore
            chunks_with_vectors = [
                {'text': chunk['text'], 'vector': embeddings[idx]}
                for idx, chunk in enumerate(chunks)
            ]
            FirebaseService.save_chunks(doc_id, chunks_with_vectors)
            
            # Get Firestore chunk IDs and prepare for ChromaDB
            firestore_chunks = FirebaseService.get_all_chunks_for_doc(doc_id)
            chunks_for_chroma = [
                {
                    'text': chunk['text'],
                    'firestore_id': firestore_chunks[idx]['id'] if idx < len(firestore_chunks) else ''
                }
                for idx, chunk in enumerate(chunks)
            ]
            
            # Add to ChromaDB
            VectorstoreService.add_chunks(doc_id, chunks_for_chroma, embeddings)
            
            logger.info(f"Document {doc_id} processed successfully with {len(chunks)} chunks")
            return {'doc_id': doc_id, 'chunks_count': len(chunks), 'status': 'processed'}
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def query_rag(query: str) -> Dict:
        """RAG query pipeline"""
        try:
            logger.debug(f"Processing RAG query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = EmbeddingService.generate_embedding(query)
            
            # Search for similar chunks
            similar_chunks = VectorstoreService.search_similar(
                query_embedding,
                top_k=settings.TOP_K_CHUNKS
            )
            
            if not similar_chunks:
                logger.info("No similar chunks found for query")
                return {
                    'answer': 'Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.',
                    'context_used': False,
                    'chunks_count': 0
                }
            
            # Get chunks from Firestore
            firestore_ids = [
                chunk['metadata'].get('firestore_id')
                for chunk in similar_chunks
                if chunk['metadata'].get('firestore_id')
            ]
            
            context_chunks = FirebaseService.get_chunks_by_ids(firestore_ids)
            
            if not context_chunks:
                logger.warning("No context chunks retrieved from Firestore")
                return {
                    'answer': 'Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.',
                    'context_used': False,
                    'chunks_count': 0
                }
            
            # Build prompt and call LLM
            prompt = PromptService.build_rag_prompt(query, context_chunks)
            answer = RAGService._call_llm(prompt)
            
            # Save chat history
            FirebaseService.save_chat_history(query, answer)
            
            logger.info(f"RAG query processed successfully with {len(context_chunks)} context chunks")
            return {
                'answer': answer,
                'context_used': True,
                'chunks_count': len(context_chunks)
            }
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _call_llm(prompt: str) -> str:
        """Call LLM (Gemini)"""
        try:
            if not settings.GOOGLE_API_KEY:
                logger.error("GOOGLE_API_KEY not configured")
                return "LLM API key not configured. Please set GOOGLE_API_KEY in environment variables."
            
            if settings.LLM_MODEL.startswith('gemini'):
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                model = genai.GenerativeModel(settings.LLM_MODEL)
                response = model.generate_content(prompt)
                
                if not response.text:
                    logger.warning("Empty response from LLM")
                    return "Không thể tạo phản hồi. Vui lòng thử lại."
                
                return response.text
            else:
                logger.warning(f"Unsupported LLM model: {settings.LLM_MODEL}")
                return "LLM model not supported. Please configure a Gemini model."
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}", exc_info=True)
            return f"Lỗi khi gọi LLM: {str(e)}"

