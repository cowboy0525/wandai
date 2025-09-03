from fastapi import APIRouter, HTTPException, Depends
import logging

from app.services.agent_orchestrator import AgentOrchestrator
from app.services.knowledge_base import KnowledgeBase
from app.models.schemas import TaskRequest, TaskResult, TaskStatus
from app.api.dependencies import agent_orchestrator_dependency, knowledge_base_dependency
from app.core.exceptions import AgentExecutionError, handle_wand_ai_exception

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/execute", response_model=TaskResult)
async def execute_task(
    task_request: TaskRequest,
    agent_orchestrator: AgentOrchestrator = Depends(agent_orchestrator_dependency),
    knowledge_base: KnowledgeBase = Depends(knowledge_base_dependency)
):
    """Execute a complex task using multiple AI agents"""
    try:
        logger.info(f"Executing task: {task_request.description}")
        
        # First, search knowledge base for relevant context
        context = await knowledge_base.search(task_request.description)
        
        # Execute task with agents
        result = await agent_orchestrator.execute_task(
            task_request.description,
            context
        )
        
        logger.info(f"Task execution completed: {result.task_id}")
        return result
    
    except AgentExecutionError as e:
        logger.error(f"Agent execution error: {e.message}")
        raise handle_wand_ai_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during task execution: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{task_id}/status", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    agent_orchestrator: AgentOrchestrator = Depends(agent_orchestrator_dependency)
):
    """Get the status of a running task"""
    try:
        logger.info(f"Getting status for task: {task_id}")
        
        status = agent_orchestrator.get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{task_id}/result", response_model=TaskResult)
async def get_task_result(
    task_id: str,
    agent_orchestrator: AgentOrchestrator = Depends(agent_orchestrator_dependency)
):
    """Get the final result of a completed task"""
    try:
        logger.info(f"Getting result for task: {task_id}")
        
        result = agent_orchestrator.get_task_result(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="Task result not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task result {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=dict)
async def list_tasks(
    agent_orchestrator: AgentOrchestrator = Depends(agent_orchestrator_dependency)
):
    """List all tasks with their statuses"""
    try:
        logger.info("Retrieving task list")
        
        tasks = agent_orchestrator.list_tasks()
        return {
            "tasks": tasks,
            "total_tasks": len(tasks)
        }
    
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
