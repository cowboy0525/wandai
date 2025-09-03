from fastapi import HTTPException
from typing import Any, Dict, Optional

class WandAIException(Exception):
    """Base exception for Wand AI application"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DocumentProcessingError(WandAIException):
    """Raised when document processing fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)

class KnowledgeBaseError(WandAIException):
    """Raised when knowledge base operations fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class AgentExecutionError(WandAIException):
    """Raised when agent execution fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class ValidationError(WandAIException):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)

def handle_wand_ai_exception(exc: WandAIException) -> HTTPException:
    """Convert WandAIException to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )
