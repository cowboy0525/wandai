from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from app.core.tools import ToolRegistry

logger = logging.getLogger(__name__)

class AgentResult:
    """Result from agent execution"""
    
    def __init__(self, 
                 success: bool,
                 output: str,
                 metadata: Dict[str, Any] = None,
                 tools_used: List[str] = None,
                 confidence: float = 1.0,
                 errors: List[str] = None):
        self.success = success
        self.output = output
        self.metadata = metadata or {}
        self.tools_used = tools_used or []
        self.confidence = confidence
        self.errors = errors or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "output": self.output,
            "metadata": self.metadata,
            "tools_used": self.tools_used,
            "confidence": self.confidence,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat()
        }

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str, capabilities: List[str], tools: List[str]):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.available_tools = tools
        self.conversation_history = []
        self.execution_count = 0
        self.success_rate = 1.0
        self.last_execution = None
    
    @abstractmethod
    async def execute(self, task: str, context: str, tool_registry: ToolRegistry) -> AgentResult:
        """Execute agent task with available tools"""
        pass
    
    async def execute_with_tools(self, agent_context: Dict[str, Any], tool_registry: ToolRegistry) -> Dict[str, Any]:
        """Execute agent with enhanced context and tool access"""
        try:
            # Extract task description from context
            task = agent_context.get("task_description", "Execute task")
            context = str(agent_context.get("shared_context", ""))
            
            # Execute the agent
            result = await self.execute(task, context, tool_registry)
            
            # Convert to dictionary format expected by orchestrator
            return {
                "output": result.output,
                "success": result.success,
                "confidence": result.confidence,
                "tools_used": result.tools_used,
                "metadata": result.metadata,
                "errors": result.errors
            }
            
        except Exception as e:
            logger.error(f"Agent {self.name} execution with tools failed: {str(e)}")
            return {
                "output": f"Execution failed: {str(e)}",
                "success": False,
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {},
                "errors": [str(e)]
            }
    
    def can_handle(self, task: str) -> bool:
        """Check if agent can handle this task type"""
        task_lower = task.lower()
        return any(capability.lower() in task_lower for capability in self.capabilities)
    
    def get_capability_score(self, task: str) -> float:
        """Get a score indicating how well this agent can handle the task"""
        task_lower = task.lower()
        score = 0.0
        
        for capability in self.capabilities:
            if capability.lower() in task_lower:
                score += 1.0
        
        # Bonus for exact matches
        if any(capability.lower() == task_lower for capability in self.capabilities):
            score += 0.5
        
        return min(score, 1.0)
    
    def add_to_history(self, task: str, result: AgentResult):
        """Add execution to conversation history"""
        self.conversation_history.append({
            "task": task,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 executions
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
        
        # Update statistics
        self.execution_count += 1
        self.last_execution = datetime.now()
        
        if result.success:
            self.success_rate = (self.success_rate * (self.execution_count - 1) + 1.0) / self.execution_count
        else:
            self.success_rate = (self.success_rate * (self.execution_count - 1)) / self.execution_count
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "success_rate": self.success_rate,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "capabilities": self.capabilities,
            "available_tools": self.available_tools
        }
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation history"""
        if not self.conversation_history:
            return "No recent activity"
        
        recent = self.conversation_history[-3:]  # Last 3 executions
        summary = []
        
        for entry in recent:
            task = entry["task"][:50] + "..." if len(entry["task"]) > 50 else entry["task"]
            status = "✅" if entry["result"]["success"] else "❌"
            summary.append(f"{status} {task}")
        
        return "\n".join(summary)
    
    async def use_tool(self, tool_name: str, params: Dict[str, Any], tool_registry: ToolRegistry) -> Dict[str, Any]:
        """Use a specific tool through the tool registry"""
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not available for this agent",
                "message": f"Agent {self.name} cannot use tool {tool_name}"
            }
        
        try:
            result = await tool_registry.execute_tool(tool_name, params)
            logger.info(f"Agent {self.name} used tool {tool_name} successfully")
            return result
        except Exception as e:
            logger.error(f"Agent {self.name} failed to use tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Tool execution failed: {str(e)}"
            }
    
    def validate_task(self, task: str) -> Dict[str, Any]:
        """Validate if the task is clear and complete"""
        validation = {
            "is_clear": True,
            "is_complete": True,
            "missing_info": [],
            "suggestions": []
        }
        
        task_lower = task.lower()
        
        # Check for common ambiguity indicators
        ambiguous_words = ["it", "this", "that", "them", "those", "here", "there"]
        if any(word in task_lower for word in ambiguous_words):
            validation["is_clear"] = False
            validation["suggestions"].append("Task contains ambiguous references - please be more specific")
        
        # Check for missing context
        if len(task.split()) < 3:
            validation["is_complete"] = False
            validation["missing_info"].append("Task description is too brief")
            validation["suggestions"].append("Provide more details about what you want to accomplish")
        
        # Check for missing parameters
        if "chart" in task_lower and "data" not in task_lower:
            validation["missing_info"].append("Chart type or data not specified")
            validation["suggestions"].append("Specify what type of chart and what data to visualize")
        
        if "analyze" in task_lower and "data" not in task_lower:
            validation["missing_info"].append("Data to analyze not specified")
            validation["suggestions"].append("Provide the data you want analyzed")
        
        return validation
    
    def generate_clarifying_questions(self, task: str) -> List[str]:
        """Generate clarifying questions for ambiguous tasks"""
        validation = self.validate_task(task)
        questions = []
        
        if not validation["is_clear"]:
            questions.append("Could you please clarify what specific information or action you need?")
        
        for missing in validation["missing_info"]:
            if "chart" in missing.lower():
                questions.append("What type of chart would you like me to create? (line, bar, pie, etc.)")
            elif "data" in missing.lower():
                questions.append("What data should I work with? Please provide the data or specify where to find it.")
            elif "analyze" in missing.lower():
                questions.append("What specific analysis would you like me to perform on the data?")
        
        if not questions:
            questions.append("Is there anything else you'd like me to clarify about this task?")
        
        return questions[:3]  # Limit to 3 questions
