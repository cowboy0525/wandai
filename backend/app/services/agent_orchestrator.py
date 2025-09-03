import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import os

from app.models.schemas import (
    AgentStatus, AgentInfo, TaskStatus, TaskResult, 
    EnrichmentSuggestion, SearchResult
)
from app.services.knowledge_base import KnowledgeBase

load_dotenv()

class AgentOrchestrator:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
        self.tasks: Dict[str, TaskStatus] = {}
        self.agents = self._initialize_agents()
        
        # OpenAI client
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def _initialize_agents(self) -> Dict[str, AgentInfo]:
        """Initialize the available AI agents"""
        return {
            "planner": AgentInfo(
                id="planner",
                name="Task Planner",
                role="Analyzes complex tasks and breaks them down into subtasks",
                status=AgentStatus.COMPLETED
            ),
            "researcher": AgentInfo(
                id="researcher",
                name="Research Agent",
                role="Gathers and analyzes information from the knowledge base",
                status=AgentStatus.COMPLETED
            ),
            "analyst": AgentInfo(
                id="analyst",
                name="Data Analyst",
                role="Processes data and generates insights",
                status=AgentStatus.COMPLETED
            ),
            "creator": AgentInfo(
                id="creator",
                name="Content Creator",
                role="Creates reports, charts, and presentations",
                status=AgentStatus.COMPLETED
            ),
            "coordinator": AgentInfo(
                id="coordinator",
                name="Task Coordinator",
                role="Coordinates between agents and ensures task completion",
                status=AgentStatus.COMPLETED
            )
        }
    
    async def execute_task(self, task_description: str, context: List[SearchResult]) -> TaskResult:
        """Execute a complex task using multiple AI agents"""
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            description=task_description,
            status=AgentStatus.PLANNING,
            agents=[],
            progress=0.0,
            estimated_completion=None,
            results={},
            errors=[]
        )
        
        try:
            start_time = datetime.now()
            
            # Phase 1: Planning
            await self._update_task_status(task_id, AgentStatus.PLANNING, 0.1)
            plan = await self._plan_task(task_description, context)
            
            # Phase 2: Execution
            await self._update_task_status(task_id, AgentStatus.EXECUTING, 0.3)
            results = await self._execute_plan(plan, context, task_id)
            
            # Phase 3: Aggregation
            await self._update_task_status(task_id, AgentStatus.EXECUTING, 0.8)
            final_result = await self._aggregate_results(results, task_description)
            
            # Phase 4: Knowledge gap analysis
            knowledge_gaps = await self._analyze_knowledge_gaps(task_description, context, final_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create final result
            task_result = TaskResult(
                task_id=task_id,
                status=AgentStatus.COMPLETED,
                final_result=final_result,
                agent_summaries=results,
                knowledge_gaps=knowledge_gaps,
                execution_time=execution_time
            )
            
            # Update final status
            await self._update_task_status(task_id, AgentStatus.COMPLETED, 1.0, final_result=final_result)
            
            return task_result
            
        except Exception as e:
            await self._update_task_status(task_id, AgentStatus.FAILED, 0.0, errors=[str(e)])
            raise e
    
    async def _plan_task(self, task_description: str, context: List[SearchResult]) -> Dict[str, Any]:
        """Use the planner agent to break down the task"""
        try:
            # Create context summary
            context_summary = "\n".join([f"- {result.filename}: {result.content[:200]}..." for result in context[:3]])
            
            prompt = f"""
            Task: {task_description}
            
            Available Context:
            {context_summary}
            
            Available Agents:
            - Research Agent: Gathers and analyzes information
            - Data Analyst: Processes data and generates insights  
            - Content Creator: Creates reports, charts, and presentations
            - Task Coordinator: Coordinates between agents
            
            Please create a detailed plan for executing this task. Include:
            1. Which agents should be involved
            2. What each agent should do
            3. The order of operations
            4. Expected outputs from each agent
            
            Format your response as a structured plan.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a task planning expert that breaks down complex business requests into executable plans."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            plan_text = response.choices[0].message.content.strip()
            
            # Parse the plan (simplified - in production, use structured output)
            return {
                "plan_text": plan_text,
                "agents_needed": self._extract_agents_from_plan(plan_text),
                "steps": self._extract_steps_from_plan(plan_text)
            }
            
        except Exception as e:
            raise Exception(f"Task planning failed: {str(e)}")
    
    async def _execute_plan(self, plan: Dict[str, Any], context: List[SearchResult], task_id: str) -> List[Dict[str, Any]]:
        """Execute the planned tasks using the specified agents"""
        results = []
        
        try:
            for step in plan.get("steps", []):
                # Update progress
                current_progress = 0.3 + (len(results) / len(plan.get("steps", []))) * 0.5
                await self._update_task_status(task_id, AgentStatus.EXECUTING, current_progress)
                
                # Execute step based on agent type
                if "research" in step.lower():
                    result = await self._execute_research_agent(step, context)
                elif "analyze" in step.lower() or "data" in step.lower():
                    result = await self._execute_analyst_agent(step, context)
                elif "create" in step.lower() or "report" in step.lower():
                    result = await self._execute_creator_agent(step, context)
                else:
                    result = await self._execute_coordinator_agent(step, context)
                
                results.append({
                    "step": step,
                    "agent": self._identify_agent_for_step(step),
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Small delay to simulate processing
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            raise Exception(f"Plan execution failed: {str(e)}")
    
    async def _execute_research_agent(self, step: str, context: List[SearchResult]) -> str:
        """Execute a research task"""
        try:
            prompt = f"""
            Research Task: {step}
            
            Available Context:
            {self._format_context_for_agent(context)}
            
            Please conduct thorough research on this topic using the available context.
            Provide a comprehensive analysis with key findings and insights.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research expert that analyzes information and provides insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Research failed: {str(e)}"
    
    async def _execute_analyst_agent(self, step: str, context: List[SearchResult]) -> str:
        """Execute a data analysis task"""
        try:
            prompt = f"""
            Analysis Task: {step}
            
            Available Data:
            {self._format_context_for_agent(context)}
            
            Please analyze this data and provide:
            1. Key trends and patterns
            2. Statistical insights
            3. Recommendations based on the analysis
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data analyst that processes information and generates insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Analysis failed: {str(e)}"
    
    async def _execute_creator_agent(self, step: str, context: List[SearchResult]) -> str:
        """Execute a content creation task"""
        try:
            prompt = f"""
            Creation Task: {step}
            
            Available Information:
            {self._format_context_for_agent(context)}
            
            Please create the requested content based on the available information.
            Make it professional, clear, and actionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a content creator that produces professional business materials."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Content creation failed: {str(e)}"
    
    async def _execute_coordinator_agent(self, step: str, context: List[SearchResult]) -> str:
        """Execute a coordination task"""
        try:
            prompt = f"""
            Coordination Task: {step}
            
            Context:
            {self._format_context_for_agent(context)}
            
            Please coordinate this task by:
            1. Identifying dependencies
            2. Ensuring all requirements are met
            3. Providing a summary of coordination actions
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project coordinator that ensures tasks are properly managed."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Coordination failed: {str(e)}"
    
    async def _aggregate_results(self, results: List[Dict[str, Any]], original_task: str) -> Dict[str, Any]:
        """Aggregate results from all agents into a final output"""
        try:
            # Create a summary of all agent outputs
            agent_outputs = "\n\n".join([
                f"**{result['agent']}**: {result['result']}"
                for result in results
            ])
            
            prompt = f"""
            Original Task: {original_task}
            
            Agent Results:
            {agent_outputs}
            
            Please create a comprehensive final result that:
            1. Addresses the original task completely
            2. Integrates insights from all agents
            3. Provides actionable recommendations
            4. Is well-structured and professional
            
            Format your response as a complete business report.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business analyst that synthesizes information into actionable reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200
            )
            
            return {
                "final_report": response.choices[0].message.content.strip(),
                "agent_contributions": len(results),
                "completion_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Result aggregation failed: {str(e)}"}
    
    async def _analyze_knowledge_gaps(self, task_description: str, context: List[SearchResult], final_result: Dict[str, Any]) -> List[EnrichmentSuggestion]:
        """Analyze what additional knowledge would improve the result"""
        try:
            prompt = f"""
            Task: {task_description}
            
            Available Context: {len(context)} documents
            Final Result: {final_result.get('final_report', 'N/A')[:500]}...
            
            Based on this task and result, what additional knowledge or data would make the output more complete or accurate?
            
            Consider:
            1. Missing data sources
            2. Additional document types needed
            3. External data that could be valuable
            4. Actions that could improve future results
            
            Provide specific, actionable suggestions.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a knowledge management expert that identifies gaps and suggests improvements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            
            # Parse suggestions (simplified)
            suggestions = []
            lines = suggestions_text.split('\n')
            for line in lines:
                if line.strip() and any(keyword in line.lower() for keyword in ['document', 'data', 'action', 'source']):
                    suggestions.append(EnrichmentSuggestion(
                        type="document" if "document" in line.lower() else "data",
                        description=line.strip(),
                        priority="medium",
                        source="AI Analysis"
                    ))
            
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            return [EnrichmentSuggestion(
                type="action",
                description=f"Knowledge gap analysis failed: {str(e)}",
                priority="low",
                source="System"
            )]
    
    def _format_context_for_agent(self, context: List[SearchResult]) -> str:
        """Format context for agent consumption"""
        if not context:
            return "No context available"
        
        formatted = []
        for i, result in enumerate(context[:3]):  # Limit to top 3 results
            formatted.append(f"{i+1}. {result.filename}: {result.content[:300]}...")
        
        return "\n".join(formatted)
    
    def _extract_agents_from_plan(self, plan_text: str) -> List[str]:
        """Extract which agents are needed from the plan"""
        agents = []
        plan_lower = plan_text.lower()
        
        if "research" in plan_lower:
            agents.append("researcher")
        if "analyze" in plan_lower or "data" in plan_lower:
            agents.append("analyst")
        if "create" in plan_lower or "report" in plan_lower:
            agents.append("creator")
        if "coordinate" in plan_lower or "manage" in plan_lower:
            agents.append("coordinator")
        
        return agents if agents else ["researcher", "analyst"]  # Default agents
    
    def _extract_steps_from_plan(self, plan_text: str) -> List[str]:
        """Extract execution steps from the plan"""
        lines = plan_text.split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in ['research', 'analyze', 'create', 'coordinate', 'gather', 'process']):
                steps.append(line)
        
        return steps if steps else ["Research the topic", "Analyze findings", "Create final report"]
    
    def _identify_agent_for_step(self, step: str) -> str:
        """Identify which agent should handle a specific step"""
        step_lower = step.lower()
        
        if "research" in step_lower or "gather" in step_lower:
            return "Research Agent"
        elif "analyze" in step_lower or "data" in step_lower:
            return "Data Analyst"
        elif "create" in step_lower or "report" in step_lower:
            return "Content Creator"
        elif "coordinate" in step_lower or "manage" in step_lower:
            return "Task Coordinator"
        else:
            return "General Agent"
    
    async def _update_task_status(self, task_id: str, status: AgentStatus, progress: float, 
                                 final_result: Optional[Dict] = None, errors: Optional[List[str]] = None):
        """Update the status of a running task"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].progress = progress
            
            if final_result:
                self.tasks[task_id].results = final_result
            
            if errors:
                self.tasks[task_id].errors = errors
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get the current status of a task"""
        return self.tasks.get(task_id, TaskStatus(
            task_id=task_id,
            description="Task not found",
            status=AgentStatus.FAILED,
            agents=[],
            progress=0.0,
            errors=["Task not found"]
        ))
