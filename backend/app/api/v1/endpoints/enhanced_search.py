from fastapi import APIRouter, HTTPException, Depends, Query
import logging
from typing import List, Optional, Dict, Any

from app.services.enhanced_knowledge_base import EnhancedKnowledgeBase
from app.models.schemas import SearchQuery, SearchResult, EnrichmentSuggestion
from app.api.dependencies import enhanced_knowledge_base_dependency

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def enhanced_search(
    search_query: SearchQuery,
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Enhanced search with knowledge gap analysis and enrichment suggestions"""
    try:
        logger.info(f"Executing enhanced search: {search_query.query}")
        
        # Perform enhanced search
        search_results = await knowledge_base.enhanced_search(
            search_query.query,
            search_query.top_k
        )
        
        # Analyze knowledge completeness
        completeness_analysis = await knowledge_base.analyze_knowledge_completeness(
            search_query.query,
            search_results
        )
        
        # Generate enrichment suggestions
        enrichment_suggestions = await knowledge_base.generate_enrichment_suggestions(
            search_query.query,
            completeness_analysis
        )
        
        # Calculate overall confidence
        overall_confidence = knowledge_base.calculate_search_confidence(
            search_results,
            completeness_analysis
        )
        
        return {
            "success": True,
            "query": search_query.query,
            "results": search_results,
            "overall_confidence": overall_confidence,
            "completeness_analysis": completeness_analysis,
            "enrichment_suggestions": enrichment_suggestions,
            "total_results": len(search_results),
            "search_metadata": {
                "search_strategy": "enhanced_semantic",
                "knowledge_coverage": completeness_analysis.get("coverage_score", 0.0),
                "quality_score": completeness_analysis.get("quality_metrics", {}).get("relevance", 0.0)
            }
        }
    
    except Exception as e:
        logger.error(f"Enhanced search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/semantic", response_model=List[SearchResult])
async def semantic_search(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Semantic search using vector embeddings"""
    try:
        logger.info(f"Executing semantic search: {query}")
        
        results = await knowledge_base.semantic_search(query, top_k)
        return results
    
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@router.post("/hybrid", response_model=List[SearchResult])
async def hybrid_search(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    semantic_weight: float = Query(0.7, ge=0.0, le=1.0, description="Weight for semantic search"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Hybrid search combining semantic and keyword approaches"""
    try:
        logger.info(f"Executing hybrid search: {query}")
        
        results = await knowledge_base.hybrid_search(
            query, 
            top_k, 
            semantic_weight
        )
        return results
    
    except Exception as e:
        logger.error(f"Hybrid search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")

@router.post("/contextual", response_model=List[SearchResult])
async def contextual_search(
    query: str = Query(..., description="Search query"),
    context: str = Query(..., description="Additional context for search"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Contextual search using additional context information"""
    try:
        logger.info(f"Executing contextual search: {query}")
        
        results = await knowledge_base.contextual_search(
            query, 
            context, 
            top_k
        )
        return results
    
    except Exception as e:
        logger.error(f"Contextual search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contextual search failed: {str(e)}")

@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    partial_query: str = Query(..., description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get search suggestions based on partial query"""
    try:
        logger.info(f"Getting search suggestions for: {partial_query}")
        
        suggestions = await knowledge_base.get_search_suggestions(
            partial_query, 
            limit
        )
        return suggestions
    
    except Exception as e:
        logger.error(f"Search suggestions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search suggestions failed: {str(e)}")

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_search_query(
    query: str = Query(..., description="Search query to analyze"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Analyze a search query for intent and complexity"""
    try:
        logger.info(f"Analyzing search query: {query}")
        
        analysis = await knowledge_base.analyze_search_query(query)
        return analysis
    
    except Exception as e:
        logger.error(f"Query analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")

@router.get("/knowledge-gaps", response_model=List[EnrichmentSuggestion])
async def identify_knowledge_gaps(
    topic: str = Query(..., description="Topic to analyze for gaps"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Identify knowledge gaps for a specific topic"""
    try:
        logger.info(f"Identifying knowledge gaps for topic: {topic}")
        
        gaps = await knowledge_base.identify_knowledge_gaps(topic)
        return gaps
    
    except Exception as e:
        logger.error(f"Knowledge gap analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Knowledge gap analysis failed: {str(e)}")

@router.post("/enrich", response_model=List[EnrichmentSuggestion])
async def generate_enrichment_plan(
    topic: str = Query(..., description="Topic to enrich"),
    priority: str = Query("medium", regex="^(low|medium|high)$", description="Enrichment priority"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Generate a plan for enriching knowledge about a topic"""
    try:
        logger.info(f"Generating enrichment plan for topic: {topic}")
        
        plan = await knowledge_base.generate_enrichment_plan(topic, priority)
        return plan
    
    except Exception as e:
        logger.error(f"Enrichment plan generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enrichment plan generation failed: {str(e)}")

@router.get("/coverage", response_model=Dict[str, Any])
async def get_knowledge_coverage(
    topic: str = Query(..., description="Topic to analyze"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get knowledge coverage analysis for a specific topic"""
    try:
        logger.info(f"Getting knowledge coverage for topic: {topic}")
        
        coverage = await knowledge_base.get_knowledge_coverage(topic)
        return coverage
    
    except Exception as e:
        logger.error(f"Knowledge coverage analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Knowledge coverage analysis failed: {str(e)}")

@router.get("/trends", response_model=List[Dict[str, Any]])
async def get_search_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get search trends and patterns over time"""
    try:
        logger.info(f"Getting search trends for last {days} days")
        
        trends = await knowledge_base.get_search_trends(days)
        return trends
    
    except Exception as e:
        logger.error(f"Search trends analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search trends analysis failed: {str(e)}")

@router.get("/popular", response_model=List[Dict[str, Any]])
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50, description="Number of popular searches"),
    period: str = Query("week", regex="^(day|week|month|year)$", description="Time period"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get most popular search queries"""
    try:
        logger.info(f"Getting popular searches for period: {period}")
        
        popular = await knowledge_base.get_popular_searches(limit, period)
        return popular
    
    except Exception as e:
        logger.error(f"Popular searches retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Popular searches retrieval failed: {str(e)}")

@router.post("/feedback", response_model=Dict[str, str])
async def submit_search_feedback(
    query: str = Query(..., description="Search query"),
    result_id: str = Query(..., description="Result ID"),
    feedback_type: str = Query(..., regex="^(relevant|irrelevant|helpful|unhelpful)$", description="Type of feedback"),
    feedback_text: Optional[str] = Query(None, description="Additional feedback text"),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Submit feedback for search results to improve future searches"""
    try:
        logger.info(f"Submitting search feedback for query: {query}")
        
        success = await knowledge_base.submit_search_feedback(
            query, 
            result_id, 
            feedback_type, 
            feedback_text
        )
        
        if success:
            return {"message": "Feedback submitted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to submit feedback")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

