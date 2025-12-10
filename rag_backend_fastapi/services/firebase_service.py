"""Firebase Service - Handle Storage and Firestore operations"""
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore, storage

from config import settings

logger = logging.getLogger(__name__)


class FirebaseService:
    _initialized = False
    _db = None
    _bucket = None

    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            logger.debug("Firebase already initialized")
            return
        
        try:
            cred_path = Path(settings.FIREBASE_CREDENTIALS_PATH)
            if not cred_path.exists():
                raise FileNotFoundError(
                    f"Firebase credentials file not found: {cred_path}"
                )
            
            cred = credentials.Certificate(str(cred_path))
            app_options = {}
            if settings.FIREBASE_STORAGE_BUCKET:
                app_options['storageBucket'] = settings.FIREBASE_STORAGE_BUCKET
            
            firebase_admin.initialize_app(cred, app_options)
            cls._db = firestore.client()
            
            if settings.FIREBASE_STORAGE_BUCKET:
                cls._bucket = storage.bucket()
                logger.info("Firebase Storage initialized")
            else:
                cls._bucket = None
                logger.info("Firebase Storage not configured (optional)")
            
            cls._initialized = True
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}", exc_info=True)
            raise Exception(f"Firebase initialization failed: {str(e)}")

    @classmethod
    def get_db(cls):
        """Get Firestore client"""
        if not cls._initialized:
            cls.initialize()
        return cls._db

    @classmethod
    def get_bucket(cls):
        """Get Storage bucket"""
        if not cls._initialized:
            cls.initialize()
        if cls._bucket is None:
            raise Exception("Firebase Storage is not configured. Set FIREBASE_STORAGE_BUCKET in config.")
        return cls._bucket

    # ========== Storage Operations ==========

    @classmethod
    def upload_file(cls, file, filename: str) -> str:
        """Upload file to Firebase Storage and return public URL (or local URL if Storage not configured)"""
        if not settings.FIREBASE_STORAGE_BUCKET:
            return f"local://{filename}"
        try:
            bucket = cls.get_bucket()
            blob = bucket.blob(f"documents/{filename}")
            blob.upload_from_file(file)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            print(f"Warning: Could not upload to Firebase Storage: {str(e)}")
            return f"local://{filename}"

    @classmethod
    def delete_file(cls, file_url: str):
        """Delete file from Firebase Storage"""
        if not settings.FIREBASE_STORAGE_BUCKET or file_url.startswith("local://"):
            return
        try:
            bucket = cls.get_bucket()
            blob_name = file_url.split('/')[-1].split('?')[0]
            blob = bucket.blob(f"documents/{blob_name}")
            blob.delete()
        except Exception as e:
            print(f"Error deleting file: {str(e)}")

    # ========== Firestore - Documents Collection ==========

    @classmethod
    def save_document_metadata(cls, doc_id: str, file_url: str, metadata: Dict) -> str:
        """Save document metadata to Firestore documents/ collection"""
        db = cls.get_db()
        doc_ref = db.collection('documents').document(doc_id)
        doc_data = {
            'file_url': file_url,
            'uploaded_at': firestore.SERVER_TIMESTAMP,
            'filename': metadata.get('filename', ''),
            'file_type': metadata.get('file_type', ''),
            'file_size': metadata.get('file_size', 0),
            **metadata
        }
        doc_ref.set(doc_data)
        return doc_id

    @classmethod
    def get_document_metadata(cls, doc_id: str) -> Optional[Dict]:
        """Get document metadata from Firestore"""
        db = cls.get_db()
        doc_ref = db.collection('documents').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    @classmethod
    def delete_document(cls, doc_id: str):
        """Delete document and all its chunks from Firestore"""
        db = cls.get_db()
        # Delete document
        db.collection('documents').document(doc_id).delete()
        # Delete all chunks for this document
        chunks_ref = db.collection('chunks').where('doc_id', '==', doc_id)
        for chunk in chunks_ref.stream():
            chunk.reference.delete()

    # ========== Firestore - Chunks Collection ==========

    @classmethod
    def save_chunks(cls, doc_id: str, chunks: List[Dict]):
        """Save chunks with vectors to Firestore chunks/ collection"""
        db = cls.get_db()
        batch = db.batch()
        
        for idx, chunk_data in enumerate(chunks):
            chunk_ref = db.collection('chunks').document()
            chunk_doc = {
                'doc_id': doc_id,
                'chunk_text': chunk_data['text'],
                'vector': chunk_data['vector'],
                'index': idx,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            batch.set(chunk_ref, chunk_doc)
        
        batch.commit()

    @classmethod
    def get_chunks_by_ids(cls, chunk_ids: List[str]) -> List[Dict]:
        """Get chunks by their Firestore document IDs"""
        db = cls.get_db()
        chunks = []
        for chunk_id in chunk_ids:
            chunk_ref = db.collection('chunks').document(chunk_id)
            chunk_doc = chunk_ref.get()
            if chunk_doc.exists:
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_doc.to_dict().get('chunk_text', ''),
                    'doc_id': chunk_doc.to_dict().get('doc_id', ''),
                    'index': chunk_doc.to_dict().get('index', 0)
                })
        return chunks

    @classmethod
    def get_all_chunks_for_doc(cls, doc_id: str) -> List[Dict]:
        """Get all chunks for a document"""
        db = cls.get_db()
        chunks_ref = db.collection('chunks').where('doc_id', '==', doc_id).order_by('index')
        chunks = []
        for chunk in chunks_ref.stream():
            chunk_data = chunk.to_dict()
            chunks.append({
                'id': chunk.id,
                'text': chunk_data.get('chunk_text', ''),
                'vector': chunk_data.get('vector', []),
                'index': chunk_data.get('index', 0)
            })
        return chunks

    # ========== Firestore - History Collection ==========

    @classmethod
    def save_chat_history(cls, question: str, answer: str, metadata: Dict = None) -> str:
        """Save chat history to Firestore history/ collection"""
        db = cls.get_db()
        chat_id = str(uuid.uuid4())
        history_ref = db.collection('history').document(chat_id)
        history_data = {
            'question': question,
            'answer': answer,
            'created_at': firestore.SERVER_TIMESTAMP,
            **(metadata or {})
        }
        history_ref.set(history_data)
        return chat_id

    @classmethod
    def get_chat_history(cls, limit: int = 50) -> List[Dict]:
        """Get recent chat history from Firestore"""
        db = cls.get_db()
        history_ref = db.collection('history').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        history = []
        for doc in history_ref.stream():
            doc_data = doc.to_dict()
            history.append({
                'id': doc.id,
                'question': doc_data.get('question', ''),
                'answer': doc_data.get('answer', ''),
                'created_at': doc_data.get('created_at')
            })
        return history

