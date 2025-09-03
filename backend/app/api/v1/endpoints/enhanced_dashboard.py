from fastapi import APIRouter, HTTPException, Depends, Query
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.services.enhanced_agent_orchestrator import EnhancedAgentOrchestrator
from app.services.enhanced_knowledge_base import EnhancedKnowledgeBase
from app.services.context_manager import ContextManager
from app.api.dependencies import (
    enhanced_agent_orchestrator_dependency, 
    enhanced_knowledge_base_dependency
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get comprehensive dashboard overview with system metrics"""
    try:
        logger.info("Getting dashboard overview")
        
        # Get system metrics
        system_metrics = await _get_system_metrics(agent_orchestrator, knowledge_base)
        
        # Get recent activity
        recent_activity = await _get_recent_activity(agent_orchestrator)
        
        # Get performance metrics
        performance_metrics = await _get_performance_metrics(agent_orchestrator)
        
        # Get knowledge base statistics
        kb_stats = await _get_knowledge_base_stats(knowledge_base)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": system_metrics,
            "recent_activity": recent_activity,
            "performance_metrics": performance_metrics,
            "knowledge_base_stats": kb_stats,
            "overall_health": _calculate_overall_health(system_metrics, performance_metrics)
        }
    
    except Exception as e:
        logger.error(f"Dashboard overview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard overview failed: {str(e)}")

@router.get("/metrics/system", response_model=Dict[str, Any])
async def get_system_metrics(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get detailed system metrics"""
    try:
        logger.info("Getting system metrics")
        
        metrics = await _get_system_metrics(agent_orchestrator, knowledge_base)
        return metrics
    
    except Exception as e:
        logger.error(f"System metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System metrics failed: {str(e)}")

@router.get("/metrics/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get detailed performance metrics"""
    try:
        logger.info("Getting performance metrics")
        
        metrics = await _get_performance_metrics(agent_orchestrator)
        return metrics
    
    except Exception as e:
        logger.error(f"Performance metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

@router.get("/agents/overview", response_model=Dict[str, Any])
async def get_agents_overview(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get comprehensive overview of all agents"""
    try:
        logger.info("Getting agents overview")
        
        # Get agent statuses
        agent_statuses = agent_orchestrator.get_all_agent_statuses()
        
        # Get agent performance
        agent_performance = {}
        for agent in agent_statuses:
            performance = agent_orchestrator.get_agent_performance(agent.name)
            if performance:
                agent_performance[agent.name] = performance
        
        # Calculate agent statistics
        total_agents = len(agent_statuses)
        active_agents = len([a for a in agent_statuses if a.status == "executing"])
        idle_agents = len([a for a in agent_statuses if a.status == "planning"])
        failed_agents = len([a for a in agent_statuses if a.status == "failed"])
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "failed_agents": failed_agents,
            "agent_statuses": agent_statuses,
            "agent_performance": agent_performance,
            "agent_distribution": {
                "executing": active_agents,
                "planning": idle_agents,
                "completed": len([a for a in agent_statuses if a.status == "completed"]),
                "failed": failed_agents
            }
        }
    
    except Exception as e:
        logger.error(f"Agents overview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agents overview failed: {str(e)}")

@router.get("/agents/{agent_name}/performance", response_model=Dict[str, Any])
async def get_agent_performance(
    agent_name: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get detailed performance metrics for a specific agent"""
    try:
        logger.info(f"Getting performance for agent: {agent_name}")
        
        performance = agent_orchestrator.get_agent_performance(agent_name)
        if not performance:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return performance
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent performance failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent performance failed: {str(e)}")

@router.get("/tasks/overview", response_model=Dict[str, Any])
async def get_tasks_overview(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get comprehensive overview of all tasks"""
    try:
        logger.info("Getting tasks overview")
        
        # Get all tasks
        tasks = agent_orchestrator.list_tasks()
        
        # Calculate task statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        failed_tasks = len([t for t in tasks if t.status == "failed"])
        running_tasks = len([t for t in tasks if t.status == "executing"])
        pending_tasks = len([t for t in tasks if t.status == "planning"])
        
        # Calculate success rate
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Get recent task activity
        recent_tasks = sorted(tasks, key=lambda x: x.updated_at, reverse=True)[:10]
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "success_rate": round(success_rate, 2),
            "recent_tasks": recent_tasks,
            "task_distribution": {
                "completed": completed_tasks,
                "failed": failed_tasks,
                "executing": running_tasks,
                "planning": pending_tasks
            }
        }
    
    except Exception as e:
        logger.error(f"Tasks overview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tasks overview failed: {str(e)}")

@router.get("/knowledge/overview", response_model=Dict[str, Any])
async def get_knowledge_overview(
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get comprehensive overview of knowledge base"""
    try:
        logger.info("Getting knowledge base overview")
        
        stats = await _get_knowledge_base_stats(knowledge_base)
        return stats
    
    except Exception as e:
        logger.error(f"Knowledge overview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Knowledge overview failed: {str(e)}")

@router.get("/analytics/trends", response_model=List[Dict[str, Any]])
async def get_analytics_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get analytics trends over time"""
    try:
        logger.info(f"Getting analytics trends for last {days} days")
        
        trends = agent_orchestrator.get_analytics_trends(days)
        return trends
    
    except Exception as e:
        logger.error(f"Analytics trends failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics trends failed: {str(e)}")

@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_performance_analytics(
    period: str = Query("week", regex="^(day|week|month|year)$", description="Time period"),
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get performance analytics for a specific period"""
    try:
        logger.info(f"Getting performance analytics for period: {period}")
        
        analytics = agent_orchestrator.get_performance_analytics(period)
        return analytics
    
    except Exception as e:
        logger.error(f"Performance analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance analytics failed: {str(e)}")

@router.get("/health/status", response_model=Dict[str, Any])
async def get_system_health(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Get system health status"""
    try:
        logger.info("Getting system health status")
        
        # Check agent health
        agent_health = _check_agent_health(agent_orchestrator)
        
        # Check knowledge base health
        kb_health = await _check_knowledge_base_health(knowledge_base)
        
        # Calculate overall health
        overall_health = _calculate_overall_health(agent_health, kb_health)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": overall_health,
            "agent_health": agent_health,
            "knowledge_base_health": kb_health,
            "recommendations": _generate_health_recommendations(agent_health, kb_health)
        }
    
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System health check failed: {str(e)}")

# Helper functions
async def _get_system_metrics(
    agent_orchestrator: EnhancedAgentOrchestrator,
    knowledge_base: EnhancedKnowledgeBase
) -> Dict[str, Any]:
    """Get comprehensive system metrics"""
    try:
        # Get basic metrics
        total_agents = len(agent_orchestrator.get_all_agent_statuses())
        total_tasks = len(agent_orchestrator.list_tasks())
        
        # Get knowledge base metrics
        kb_stats = await _get_knowledge_base_stats(knowledge_base)
        
        return {
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "total_documents": kb_stats.get("total_documents", 0),
            "system_uptime": "24 hours",  # Placeholder
            "active_connections": 0,  # Placeholder
            "memory_usage": "512 MB",  # Placeholder
            "cpu_usage": "15%"  # Placeholder
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        return {}

async def _get_recent_activity(
    agent_orchestrator: EnhancedAgentOrchestrator
) -> List[Dict[str, Any]]:
    """Get recent system activity"""
    try:
        # Get recent tasks
        recent_tasks = agent_orchestrator.list_tasks()[-10:]  # Last 10 tasks
        
        activity = []
        for task in recent_tasks:
            activity.append({
                "type": "task",
                "description": task.description,
                "status": task.status,
                "timestamp": task.updated_at.isoformat(),
                "agent_count": len(task.agents)
            })
        
        return activity
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return []

async def _get_performance_metrics(
    agent_orchestrator: EnhancedAgentOrchestrator
) -> Dict[str, Any]:
    """Get performance metrics"""
    try:
        analytics = agent_orchestrator.get_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return {}

async def _get_knowledge_base_stats(
    knowledge_base: EnhancedKnowledgeBase
) -> Dict[str, Any]:
    """Get knowledge base statistics"""
    try:
        # This would be implemented in the enhanced knowledge base
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "index_size": "0 MB",
            "last_updated": datetime.now().isoformat(),
            "search_queries_today": 0,
            "average_search_time": "0.1s"
        }
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {str(e)}")
        return {}

def _calculate_overall_health(
    system_metrics: Dict[str, Any],
    performance_metrics: Dict[str, Any]
) -> str:
    """Calculate overall system health"""
    try:
        # Simple health calculation based on metrics
        if not system_metrics or not performance_metrics:
            return "unknown"
        
        # Check for critical issues
        if system_metrics.get("failed_agents", 0) > 0:
            return "poor"
        
        # Check performance
        success_rate = performance_metrics.get("success_rate", 0)
        if success_rate >= 90:
            return "excellent"
        elif success_rate >= 75:
            return "good"
        elif success_rate >= 50:
            return "fair"
        else:
            return "poor"
    
    except Exception:
        return "unknown"

def _check_agent_health(
    agent_orchestrator: EnhancedAgentOrchestrator
) -> Dict[str, Any]:
    """Check agent health status"""
    try:
        agents = agent_orchestrator.get_all_agent_statuses()
        
        healthy_agents = len([a for a in agents if a.status != "failed"])
        total_agents = len(agents)
        
        return {
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "failed_agents": total_agents - healthy_agents,
            "health_percentage": (healthy_agents / total_agents * 100) if total_agents > 0 else 0,
            "status": "healthy" if healthy_agents == total_agents else "degraded"
        }
    except Exception as e:
        logger.error(f"Error checking agent health: {str(e)}")
        return {"status": "unknown", "error": str(e)}

async def _check_knowledge_base_health(
    knowledge_base: EnhancedKnowledgeBase
) -> Dict[str, Any]:
    """Check knowledge base health status"""
    try:
        # This would be implemented in the enhanced knowledge base
        return {
            "status": "healthy",
            "index_health": "good",
            "storage_health": "good",
            "last_backup": "24 hours ago",
            "error_count": 0
        }
    except Exception as e:
        logger.error(f"Error checking knowledge base health: {str(e)}")
        return {"status": "unknown", "error": str(e)}

def _generate_health_recommendations(
    agent_health: Dict[str, Any],
    kb_health: Dict[str, Any]
) -> List[str]:
    """Generate health recommendations"""
    recommendations = []
    
    # Agent recommendations
    if agent_health.get("failed_agents", 0) > 0:
        recommendations.append("Investigate failed agents and restart if necessary")
    
    if agent_health.get("health_percentage", 100) < 80:
        recommendations.append("Monitor agent performance and optimize configurations")
    
    # Knowledge base recommendations
    if kb_health.get("status") != "healthy":
        recommendations.append("Check knowledge base index and storage health")
    
    if not recommendations:
        recommendations.append("System is operating normally")
    
    return recommendations

