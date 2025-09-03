import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import os
import logging
import json

from app.models.schemas import (
    AgentStatus, AgentInfo, TaskStatus, TaskResult, 
    EnrichmentSuggestion, SearchResult
)
from app.services.enhanced_knowledge_base import EnhancedKnowledgeBase
from app.services.agents import (
    PlannerAgent, ResearchAgent, AnalysisAgent, 
    CreatorAgent, CoordinatorAgent
)
from app.core.tools import ToolRegistry
from app.services.context_manager import ContextManager

logger = logging.getLogger(__name__)

class EnhancedAgentOrchestrator:
    """Enhanced agent orchestrator with intelligent agent selection and tool integration"""
    
    def __init__(self, knowledge_base: EnhancedKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.tasks: Dict[str, TaskStatus] = {}
        self.tool_registry = ToolRegistry()
        self.context_manager = ContextManager()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # OpenAI client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Task execution statistics
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0
        }
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all available agents"""
        return {
            "planner": PlannerAgent(),
            "research": ResearchAgent(),
            "analysis": AnalysisAgent(),
            "creator": CreatorAgent(),
            "coordinator": CoordinatorAgent()
        }
    
    async def execute_task(self, task_description: str, context: List[SearchResult] = None) -> TaskResult:
        """Execute a complex task using multiple AI agents with enhanced orchestration"""
        task_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Initialize task status
        self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            description=task_description,
            status=AgentStatus.PLANNING,
            created_at=start_time,
            updated_at=start_time,
            agents=[],
            progress=0.0
        )
        
        try:
            # Phase 1: Task Planning and Agent Selection
            await self._update_task_status(task_id, AgentStatus.PLANNING, 0.1)
            plan_result = await self._plan_task_with_agents(task_description, context)
            
            if not plan_result["success"]:
                raise Exception(f"Task planning failed: {plan_result['error']}")
            
            # Phase 2: Intelligent Agent Execution with Tool Integration
            await self._update_task_status(task_id, AgentStatus.EXECUTING, 0.3)
            execution_results = await self._execute_with_intelligent_agents(
                task_id, plan_result["plan"], context
            )
            
            # Phase 3: Result Aggregation and Quality Check
            await self._update_task_status(task_id, AgentStatus.EXECUTING, 0.8)
            final_result = await self._aggregate_results_enhanced(
                task_description, execution_results, context
            )
            
            # Phase 4: Knowledge Gap Analysis
            knowledge_gaps = await self._analyze_knowledge_gaps_enhanced(
                task_description, context, final_result
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create final result
            task_result = TaskResult(
                task_id=task_id,
                status=AgentStatus.COMPLETED,
                final_result=final_result,
                agent_summaries=execution_results,
                knowledge_gaps=knowledge_gaps,
                execution_time=execution_time,
                created_at=start_time,
                completed_at=datetime.now()
            )
            
            # Update final status
            await self._update_task_status(task_id, AgentStatus.COMPLETED, 1.0, final_result)
            
            # Update statistics
            self._update_statistics(True, execution_time)
            
            return task_result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_task_status(task_id, AgentStatus.FAILED, 0.0, errors=[str(e)])
            
            # Update statistics
            self._update_statistics(False, execution_time)
            
            raise Exception(f"Task execution failed: {str(e)}")
    
    async def _plan_task_with_agents(self, task_description: str, context: List[SearchResult] = None) -> Dict[str, Any]:
        """Plan task execution with intelligent agent selection"""
        try:
            # Use planner agent to create execution plan
            planner = self.agents["planner"]
            plan_result = await planner.execute(task_description, self._format_context(context), self.tool_registry)
            
            if not plan_result.success:
                return {"success": False, "error": plan_result.output}
            
            # Extract structured plan
            structured_plan = plan_result.metadata.get("structured_plan", {})
            
            # Select appropriate agents based on plan
            selected_agents = self._select_agents_for_task(task_description, structured_plan)
            
            return {
                "success": True,
                "plan": structured_plan,
                "selected_agents": selected_agents,
                "plan_text": plan_result.output
            }
            
        except Exception as e:
            logger.error(f"Task planning failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _select_agents_for_task(self, task_description: str, structured_plan: Dict[str, Any]) -> List[str]:
        """Intelligently select agents for task execution"""
        task_lower = task_description.lower()
        selected_agents = []
        
        # Always include planner for complex tasks
        if len(task_description.split()) > 10:
            selected_agents.append("planner")
        
        # Select agents based on task requirements
        if any(word in task_lower for word in ["research", "find", "gather", "search"]):
            selected_agents.append("research")
        
        if any(word in task_lower for word in ["analyze", "analyze", "data", "trend", "pattern"]):
            selected_agents.append("analysis")
        
        if any(word in task_lower for word in ["create", "generate", "make", "build", "chart", "report"]):
            selected_agents.append("creator")
        
        # Always include coordinator for multi-agent tasks
        if len(selected_agents) > 1:
            selected_agents.append("coordinator")
        
        # Ensure at least 2 agents are selected
        if len(selected_agents) < 2:
            if "research" not in selected_agents:
                selected_agents.append("research")
            if "analysis" not in selected_agents:
                selected_agents.append("analysis")
        
        return selected_agents
    
    async def _execute_with_intelligent_agents(self, task_id: str, plan: Dict[str, Any], 
                                             context: List[SearchResult]) -> List[Dict[str, Any]]:
        """Execute task using intelligent agent orchestration with tool integration"""
        execution_results = []
        selected_agents = plan.get("selected_agents", ["research", "analysis"])
        
        try:
            # Initialize shared context
            shared_context = self.context_manager.create_context(task_id, context)
            
            for i, agent_name in enumerate(selected_agents):
                if agent_name not in self.agents:
                    logger.warning(f"Agent {agent_name} not found, skipping")
                    continue
                
                # Update progress
                progress = 0.3 + (i * 0.4 / len(selected_agents))
                await self._update_task_status(task_id, AgentStatus.EXECUTING, progress)
                
                # Get agent
                agent = self.agents[agent_name]
                
                # Execute agent with tool access and shared context
                agent_result = await self._execute_agent_with_tools(
                    agent, agent_name, plan, shared_context, context
                )
                
                # Store result
                execution_results.append({
                    "agent": agent_name,
                    "result": agent_result,
                    "timestamp": datetime.now().isoformat(),
                    "tools_used": agent_result.get("tools_used", []),
                    "confidence": agent_result.get("confidence", 0.7)
                })
                
                # Update shared context with agent results
                shared_context = self.context_manager.update_context(
                    task_id, agent_name, agent_result
                )
                
                # Validate agent output to prevent hallucination
                validation_result = await self._validate_agent_output(
                    agent_name, agent_result, context
                )
                
                if not validation_result["valid"]:
                    logger.warning(f"Agent {agent_name} output validation failed: {validation_result['reason']}")
                    # Mark as low confidence but continue
                    execution_results[-1]["confidence"] *= 0.5
                
                # Add validation info to result
                execution_results[-1]["validation"] = validation_result
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            raise Exception(f"Agent execution failed: {str(e)}")
    
    async def _execute_agent_with_tools(self, agent: Any, agent_name: str, plan: Dict[str, Any], 
                                       shared_context: Dict[str, Any], context: List[SearchResult]) -> Dict[str, Any]:
        """Execute an agent with access to tools and shared context"""
        try:
            # Prepare agent context
            agent_context = {
                "task_description": plan.get("description", ""),
                "shared_context": shared_context,
                "available_tools": self.tool_registry.get_available_tools(),
                "previous_results": shared_context.get("agent_results", {}),
                "knowledge_base_context": context
            }
            
            # Execute agent
            if hasattr(agent, 'execute_with_tools'):
                result = await agent.execute_with_tools(agent_context, self.tool_registry)
            else:
                # Fallback to basic execution
                result = await agent.execute(plan.get("description", ""), agent_context)
            
            # Extract tool usage
            tools_used = []
            if isinstance(result, dict) and "tools_used" in result:
                tools_used = result["tools_used"]
            
            # Add metadata
            result["agent_name"] = agent_name
            result["execution_timestamp"] = datetime.now().isoformat()
            result["tools_used"] = tools_used
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent_name} execution failed: {str(e)}")
            return {
                "error": str(e),
                "agent_name": agent_name,
                "tools_used": [],
                "confidence": 0.0
            }
    
    async def _validate_agent_output(self, agent_name: str, agent_result: Dict[str, Any], 
                                    context: List[SearchResult]) -> Dict[str, Any]:
        """Validate agent output to prevent hallucination"""
        try:
            # Check if agent used tools (more reliable)
            tools_used = agent_result.get("tools_used", [])
            if tools_used:
                return {"valid": True, "reason": "Tools were used", "confidence": "high"}
            
            # Check if output matches available context
            output = agent_result.get("output", "")
            if not output:
                return {"valid": False, "reason": "No output generated", "confidence": "low"}
            
            # Use fact-checking tool if available
            if "fact_checker" in self.tool_registry.tools:
                fact_check_result = await self.tool_registry.execute_tool(
                    "fact_checker",
                    claim=output[:500],  # Limit for efficiency
                    context=self._format_context(context),
                    sources=[result.document_id for result in context]
                )
                
                if fact_check_result["success"]:
                    confidence = fact_check_result["result"].get("confidence", 0.5)
                    return {
                        "valid": confidence > 0.6,
                        "reason": f"Fact-check confidence: {confidence}",
                        "confidence": "high" if confidence > 0.6 else "medium"
                    }
            
            # Fallback validation
            context_text = self._format_context(context)
            if context_text and len(context_text) > 100:
                # Simple overlap check
                output_words = set(output.lower().split())
                context_words = set(context_text.lower().split())
                overlap = len(output_words.intersection(context_words))
                
                if overlap > len(output_words) * 0.3:  # 30% overlap threshold
                    return {"valid": True, "reason": "Good context overlap", "confidence": "medium"}
                else:
                    return {"valid": False, "reason": "Low context overlap", "confidence": "low"}
            
            return {"valid": True, "reason": "Basic validation passed", "confidence": "low"}
            
        except Exception as e:
            logger.error(f"Agent output validation failed: {str(e)}")
            return {"valid": True, "reason": "Validation failed, assuming valid", "confidence": "low"}
    
    async def _aggregate_results_enhanced(self, task_description: str, execution_results: List[Dict[str, Any]], 
                                         context: List[SearchResult]) -> Dict[str, Any]:
        """Aggregate results from multiple agents with enhanced quality control"""
        try:
            # Filter out failed executions
            successful_results = [r for r in execution_results if "error" not in r]
            
            if not successful_results:
                return {
                    "status": "failed",
                    "reason": "No successful agent executions",
                    "summary": "Task execution failed across all agents"
                }
            
            # Aggregate agent outputs
            aggregated_output = {
                "task_description": task_description,
                "execution_summary": {},
                "final_result": "",
                "confidence_scores": {},
                "tools_used": [],
                "validation_status": {}
            }
            
            # Collect results from each agent
            for result in successful_results:
                agent_name = result.get("agent_name", "unknown")
                output = result.get("output", result.get("result", ""))
                confidence = result.get("confidence", 0.5)
                tools = result.get("tools_used", [])
                validation = result.get("validation", {})
                
                aggregated_output["execution_summary"][agent_name] = {
                    "output": output,
                    "confidence": confidence,
                    "tools_used": tools,
                    "validation": validation
                }
                
                aggregated_output["confidence_scores"][agent_name] = confidence
                aggregated_output["tools_used"].extend(tools)
                aggregated_output["validation_status"][agent_name] = validation
            
            # Generate final result using coordinator agent
            coordinator = self.agents.get("coordinator")
            if coordinator:
                final_result = await coordinator.synthesize_results(
                    task_description, successful_results, context
                )
                aggregated_output["final_result"] = final_result
            else:
                # Fallback synthesis
                aggregated_output["final_result"] = self._fallback_synthesis(successful_results)
            
            # Calculate overall confidence
            overall_confidence = sum(aggregated_output["confidence_scores"].values()) / len(aggregated_output["confidence_scores"])
            aggregated_output["overall_confidence"] = overall_confidence
            
            return aggregated_output
            
        except Exception as e:
            logger.error(f"Result aggregation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "summary": "Failed to aggregate agent results"
            }
    
    def _fallback_synthesis(self, execution_results: List[Dict[str, Any]]) -> str:
        """Fallback method to synthesize agent results"""
        try:
            synthesis = "Task execution completed with the following results:\n\n"
            
            for result in execution_results:
                agent_name = result.get("agent_name", "Unknown Agent")
                output = result.get("output", result.get("result", "No output"))
                confidence = result.get("confidence", 0.0)
                
                synthesis += f"**{agent_name}** (Confidence: {confidence:.2f}):\n{output}\n\n"
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Fallback synthesis failed: {str(e)}")
            return "Failed to synthesize results"
    
    async def _analyze_knowledge_gaps_enhanced(self, task_description: str, context: List[SearchResult], 
                                             final_result: Dict[str, Any]) -> List[EnrichmentSuggestion]:
        """Analyze knowledge gaps and suggest enrichment"""
        try:
            # Use knowledge base to suggest enrichment
            if hasattr(self.knowledge_base, 'suggest_enrichment'):
                suggestions = await self.knowledge_base.suggest_enrichment(
                    task_description, context, final_result
                )
                return suggestions
            
            # Fallback suggestions
            return [
                EnrichmentSuggestion(
                    type="document_upload",
                    description="Upload additional documents related to your task",
                    priority="medium",
                    expected_impact="high"
                ),
                EnrichmentSuggestion(
                    type="external_data",
                    description="Consider integrating external data sources",
                priority="low",
                    expected_impact="medium"
                )
            ]
            
        except Exception as e:
            logger.error(f"Knowledge gap analysis failed: {str(e)}")
            return []
    
    def _format_context(self, context: List[SearchResult] = None) -> str:
        """Format context for agent consumption"""
        if not context:
            return ""
        
        try:
            context_parts = []
            for i, result in enumerate(context[:3]):  # Limit to top 3 results
                content = result.content if hasattr(result, 'content') else str(result)
                context_parts.append(f"Context {i+1}: {content[:300]}...")
            
            return "\n\n".join(context_parts)
        
        except Exception as e:
            logger.error(f"Context formatting failed: {str(e)}")
            return str(context)
    
    async def _update_task_status(self, task_id: str, status: AgentStatus, progress: float, 
                                 result: Any = None, errors: List[str] = None):
        """Update task status with progress and results"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].progress = progress
            self.tasks[task_id].updated_at = datetime.now()
            
            if result:
                self.tasks[task_id].result = result
            
            if errors:
                self.tasks[task_id].errors = errors
    
    def _update_statistics(self, success: bool, execution_time: float):
        """Update execution statistics"""
        self.stats["total_tasks"] += 1
        
        if success:
            self.stats["successful_tasks"] += 1
        else:
            self.stats["failed_tasks"] += 1
        
        # Update average execution time
        current_avg = self.stats["average_execution_time"]
        total_tasks = self.stats["total_tasks"]
        
        self.stats["average_execution_time"] = (
            (current_avg * (total_tasks - 1) + execution_time) / total_tasks
        )
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get current status of a task"""
        return self.tasks.get(task_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return self.stats.copy()

    async def execute_task_with_progress(self, task_description: str, context: List[SearchResult] = None):
        """Execute task with streaming progress updates"""
        task_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Initialize task
            self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            description=task_description,
            status=AgentStatus.PLANNING,
            created_at=start_time,
            updated_at=start_time,
            agents=[],
            progress=0.0
        )
        
            # Yield initial status
            yield {
                "type": "status_update",
                "task_id": task_id,
                "status": "PLANNING",
                "progress": 0.0,
                "message": "Starting task planning..."
            }
            
            # Phase 1: Planning
            plan_result = await self._plan_task_with_agents(task_description, context)
            if not plan_result["success"]:
                yield {
                    "type": "error",
                    "task_id": task_id,
                    "message": f"Planning failed: {plan_result['error']}"
                }
                return
            
            yield {
                "type": "status_update",
                "task_id": task_id,
                "status": "EXECUTING",
                "progress": 0.3,
                "message": "Planning completed, starting execution..."
            }
            
            # Phase 2: Execution
            execution_results = await self._execute_with_intelligent_agents(
                task_id, plan_result["plan"], context
            )
            
            yield {
                "type": "status_update",
                "task_id": task_id,
                "status": "EXECUTING",
                "progress": 0.8,
                "message": "Agent execution completed, synthesizing results..."
            }
            
            # Phase 3: Synthesis
            final_result = await self._aggregate_results_enhanced(
                task_description, execution_results, context
            )
            
            # Final status
            yield {
                "type": "completion",
                "task_id": task_id,
                "status": "COMPLETED",
                "progress": 1.0,
                "result": final_result,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "task_id": task_id,
                "message": f"Task execution failed: {str(e)}"
            }
    
    async def ask_clarifying_questions(self, task_description: str) -> List[str]:
        """Ask clarifying questions for ambiguous tasks"""
        try:
            # Use OpenAI to generate clarifying questions
            prompt = f"""
            Analyze this task description and generate 2-3 clarifying questions to help understand the requirements better:
            
            Task: {task_description}
            
            Focus on:
            1. Missing specific details
            2. Ambiguous requirements
            3. Scope clarification
            4. Success criteria
            
            Format as a simple list of questions.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            questions = response.choices[0].message.content.strip().split('\n')
            # Clean up questions
            questions = [q.strip().lstrip('1234567890.- ') for q in questions if q.strip()]
            
            return questions[:3]  # Limit to 3 questions
            
        except Exception as e:
            logger.error(f"Clarifying questions generation failed: {str(e)}")
            return [
                "What specific outcome are you looking for?",
                "What is the scope and timeline for this task?",
                "Are there any specific constraints or requirements?"
            ]
