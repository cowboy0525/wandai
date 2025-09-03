from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import logging

from app.services.knowledge_base import KnowledgeBase
from app.models.schemas import DocumentMetadata
from app.api.dependencies import knowledge_base_dependency
from app.core.exceptions import DocumentProcessingError, handle_wand_ai_exception

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    knowledge_base: KnowledgeBase = Depends(knowledge_base_dependency)
):
    """Upload and process a document for the knowledge base"""
    try:
        logger.info(f"Processing document upload: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        allowed_extensions = ('.pdf', '.txt', '.md')
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Process and store document
        doc_id = await knowledge_base.add_document(file)
        
        logger.info(f"Document uploaded successfully: {doc_id}")
        return {
            "message": "Document uploaded successfully", 
            "doc_id": doc_id,
            "filename": file.filename
        }
    
    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {e.message}")
        raise handle_wand_ai_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during document upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=dict)
async def list_documents(
    knowledge_base: KnowledgeBase = Depends(knowledge_base_dependency)
):
    """List all documents in the knowledge base"""
    try:
        logger.info("Retrieving document list")
        documents = knowledge_base.list_documents()
        return {"documents": documents}
    
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{doc_id}", response_model=DocumentMetadata)
async def get_document(
    doc_id: str,
    knowledge_base: KnowledgeBase = Depends(knowledge_base_dependency)
):
    """Get specific document information"""
    try:
        logger.info(f"Retrieving document: {doc_id}")
        document = knowledge_base.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
