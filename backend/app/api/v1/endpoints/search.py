from fastapi import APIRouter, HTTPException, Depends
import logging

from app.services.knowledge_base import KnowledgeBase
from app.models.schemas import SearchQuery
from app.api.dependencies import knowledge_base_dependency
from app.core.exceptions import KnowledgeBaseError, handle_wand_ai_exception

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def search_knowledge_base(
    query: SearchQuery,
    knowledge_base: KnowledgeBase = Depends(knowledge_base_dependency)
):
    """Search the knowledge base with natural language"""
    try:
        logger.info(f"Processing search query: {query.query}")
        
        # Perform search
        results = await knowledge_base.search(query.query, query.top_k)
        
        # Get enrichment suggestions
        suggestions = knowledge_base.get_enrichment_suggestions(query.query)
        
        logger.info(f"Search completed with {len(results)} results")
        
        return {
            "query": query.query,
            "results": results,
            "suggestions": suggestions,
            "total_results": len(results)
        }
    
    except KnowledgeBaseError as e:
        logger.error(f"Knowledge base error during search: {e.message}")
        raise handle_wand_ai_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/suggestions")
async def get_search_suggestions(
    query: str,
    knowledge_base: KnowledgeBase = Depends(knowledge_base_dependency)
):
    """Get search suggestions and enrichment recommendations"""
    try:
        logger.info(f"Getting suggestions for query: {query}")
        
        suggestions = knowledge_base.get_enrichment_suggestions(query)
        
        return {
            "query": query,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
    
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
