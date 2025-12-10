"""API Routes for FastAPI backend"""
import logging
import uuid
from io import BytesIO
from typing import Optional

import PyPDF2
import docx
from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from api.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    HistoryResponse,
    UploadResponse,
)
from services.firebase_service import FirebaseService
from services.rag_service import RAGService
from services.vectorstore_service import VectorstoreService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload-document", response_model=UploadResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """Upload document và xử lý RAG pipeline"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    filename = file.filename
    file_type = filename.split('.')[-1].lower() if '.' in filename else ''
    
    allowed_types = ['pdf', 'txt', 'md', 'docx']
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_type}' not allowed. Allowed types: {allowed_types}"
        )
    
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        file_content = ""
        
        try:
            if file_type == 'pdf':
                pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
                file_content = "\n".join([
                    page.extract_text() for page in pdf_reader.pages if page.extract_text()
                ])
            elif file_type in ['txt', 'md']:
                file_content = contents.decode('utf-8')
            elif file_type == 'docx':
                doc = docx.Document(BytesIO(contents))
                file_content = "\n".join([para.text for para in doc.paragraphs if para.text])
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not read file content: {str(e)}"
            )
        
        if not file_content.strip():
            raise HTTPException(
                status_code=400,
                detail="File is empty or could not extract text content"
            )
        
        file.file.seek(0)
        file_url = FirebaseService.upload_file(file.file, filename)
        doc_id = str(uuid.uuid4())
        
        metadata = {
            'filename': filename,
            'file_type': file_type,
            'file_size': len(contents)
        }
        
        FirebaseService.save_document_metadata(doc_id, file_url, metadata)
        result = RAGService.process_document(file_content, doc_id, metadata)
        
        logger.info(f"Document uploaded successfully: {doc_id} ({result['chunks_count']} chunks)")
        
        return UploadResponse(
            doc_id=doc_id,
            file_url=file_url,
            chunks_count=result['chunks_count'],
            status='success',
            message='Document uploaded and processed successfully'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat với RAG"""
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    if len(query) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Query is too long. Maximum length is 5000 characters"
        )
    
    try:
        logger.info(f"Processing chat query: {query[:100]}...")
        result = RAGService.query_rag(query)
        
        return ChatResponse(
            answer=result['answer'],
            context_used=result['context_used'],
            chunks_count=result.get('chunks_count', 0)
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/history", response_model=HistoryResponse)
async def get_history(limit: int = Query(50, ge=1, le=100)):
    """Lấy lịch sử chat từ Firestore"""
    try:
        history_data = FirebaseService.get_chat_history(limit=limit)
        history_items = []
        
        for item in history_data:
            created_at = item.get('created_at')
            if created_at:
                if hasattr(created_at, 'isoformat'):
                    created_at = created_at.isoformat()
                else:
                    created_at = str(created_at)
            
            history_items.append({
                'id': item['id'],
                'question': item['question'],
                'answer': item['answer'],
                'created_at': created_at
            })
        
        logger.info(f"Retrieved {len(history_items)} history items")
        return HistoryResponse(history=history_items, count=len(history_items))
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        stats = VectorstoreService.get_collection_stats()
        return HealthResponse(status='healthy', vectorstore=stats)
    except Exception as e:
        return HealthResponse(status='error', vectorstore={'error': str(e)})

