from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional

from app.services.enhanced_agent_orchestrator import EnhancedAgentOrchestrator
from app.services.enhanced_knowledge_base import EnhancedKnowledgeBase
from app.models.schemas import TaskRequest, TaskResult, TaskStatus
from app.api.dependencies import enhanced_agent_orchestrator_dependency, enhanced_knowledge_base_dependency
from app.core.exceptions import AgentExecutionError, handle_wand_ai_exception

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections for real-time updates
active_connections: Dict[str, WebSocket] = {}

@router.post("/execute", response_model=TaskResult)
async def execute_enhanced_task(
    task_request: TaskRequest,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Execute a complex task using the enhanced multi-agent system"""
    try:
        logger.info(f"Executing enhanced task: {task_request.description}")
        
        # Search knowledge base for relevant context
        context = await knowledge_base.search(task_request.description)
        
        # Execute task with enhanced agent orchestration
        result = await agent_orchestrator.execute_task(
            task_request.description,
            context
        )
        
        logger.info(f"Enhanced task execution completed: {result.task_id}")
        return result
    
    except AgentExecutionError as e:
        logger.error(f"Enhanced agent execution error: {e.message}")
        raise handle_wand_ai_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during enhanced task execution: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/execute/stream")
async def execute_task_with_streaming(
    task_request: TaskRequest,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency),
    knowledge_base: EnhancedKnowledgeBase = Depends(enhanced_knowledge_base_dependency)
):
    """Execute a task with streaming progress updates"""
    
    async def generate_progress_stream():
        try:
            # Search knowledge base for relevant context
            context = await knowledge_base.search(task_request.description)
            
            # Execute task with streaming updates
            async for progress_update in agent_orchestrator.execute_task_with_progress(
                task_request.description,
                context
            ):
                yield f"data: {json.dumps(progress_update)}\n\n"
                
        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e),
                "timestamp": "now"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.websocket("/ws/{task_id}")
async def websocket_task_progress(
    websocket: WebSocket,
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """WebSocket endpoint for real-time task progress updates"""
    await websocket.accept()
    active_connections[task_id] = websocket
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "task_id": task_id,
            "message": "WebSocket connection established"
        }))
        
        # Monitor task progress
        while True:
            # Get current task status
            task_status = agent_orchestrator.get_task_status(task_id)
            if task_status:
                await websocket.send_text(json.dumps({
                    "type": "progress_update",
                    "task_id": task_id,
                    "status": task_status.dict()
                }))
            
            # Wait before next update
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "task_id": task_id,
                "message": str(e)
            }))
        except:
            pass
    finally:
        if task_id in active_connections:
            del active_connections[task_id]

@router.get("/{task_id}/status", response_model=TaskStatus)
async def get_enhanced_task_status(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get the detailed status of a running task with agent information"""
    try:
        logger.info(f"Getting enhanced status for task: {task_id}")
        
        status = agent_orchestrator.get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced task status {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{task_id}/result", response_model=TaskResult)
async def get_enhanced_task_result(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get the final result of a completed task with agent outputs"""
    try:
        logger.info(f"Getting enhanced result for task: {task_id}")
        
        result = agent_orchestrator.get_task_result(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="Task result not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced task result {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{task_id}/agents")
async def get_task_agent_status(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get detailed status of all agents involved in a task"""
    try:
        logger.info(f"Getting agent status for task: {task_id}")
        
        agent_statuses = agent_orchestrator.get_task_agent_statuses(task_id)
        if not agent_statuses:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task_id,
            "agents": agent_statuses,
            "total_agents": len(agent_statuses)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent statuses for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{task_id}/workflow")
async def get_task_workflow(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get the workflow execution details for a task"""
    try:
        logger.info(f"Getting workflow for task: {task_id}")
        
        workflow = agent_orchestrator.get_task_workflow(task_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Task workflow not found")
        
        return workflow
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{task_id}/pause")
async def pause_task(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Pause a running task"""
    try:
        logger.info(f"Pausing task: {task_id}")
        
        success = agent_orchestrator.pause_task(task_id)
        if not success:
            raise HTTPException(status_code=400, detail="Task cannot be paused")
        
        return {"message": "Task paused successfully", "task_id": task_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{task_id}/resume")
async def resume_task(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Resume a paused task"""
    try:
        logger.info(f"Resuming task: {task_id}")
        
        success = agent_orchestrator.resume_task(task_id)
        if not success:
            raise HTTPException(status_code=400, detail="Task cannot be resumed")
        
        return {"message": "Task resumed successfully", "task_id": task_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Cancel a running or paused task"""
    try:
        logger.info(f"Cancelling task: {task_id}")
        
        success = agent_orchestrator.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=400, detail="Task cannot be cancelled")
        
        return {"message": "Task cancelled successfully", "task_id": task_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=dict)
async def list_enhanced_tasks(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """List all tasks with enhanced status information"""
    try:
        logger.info("Retrieving enhanced task list")
        
        tasks = agent_orchestrator.list_tasks()
        task_summaries = []
        
        for task in tasks:
            summary = {
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "agent_count": len(task.agents)
            }
            task_summaries.append(summary)
        
        return {
            "tasks": task_summaries,
            "total_tasks": len(task_summaries),
            "status_distribution": {
                "planning": len([t for t in task_summaries if t["status"] == "planning"]),
                "executing": len([t for t in task_summaries if t["status"] == "executing"]),
                "completed": len([t for t in task_summaries if t["status"] == "completed"]),
                "failed": len([t for t in task_summaries if t["status"] == "failed"])
            }
        }
    
    except Exception as e:
        logger.error(f"Error retrieving enhanced tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics/overview")
async def get_task_analytics(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get analytics overview of all tasks and agent performance"""
    try:
        logger.info("Retrieving task analytics")
        
        analytics = agent_orchestrator.get_analytics()
        return analytics
    
    except Exception as e:
        logger.error(f"Error retrieving task analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents/status")
async def get_all_agent_statuses(
    agent_orchestrator: EnhancedAgentOrchestrator = Depends(enhanced_agent_orchestrator_dependency)
):
    """Get status of all available agents"""
    try:
        logger.info("Retrieving all agent statuses")
        
        agent_statuses = agent_orchestrator.get_all_agent_statuses()
        return {
            "agents": agent_statuses,
            "total_agents": len(agent_statuses),
            "active_agents": len([a for a in agent_statuses if a.status == "executing"]),
            "idle_agents": len([a for a in agent_statuses if a.status == "planning"])
        }
    
    except Exception as e:
        logger.error(f"Error retrieving agent statuses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

