import openai
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Agent responsible for planning and breaking down complex tasks"""
    
    def __init__(self):
        super().__init__(
            name="Task Planner",
            role="Analyzes complex tasks and breaks them down into executable subtasks",
            capabilities=["planning", "task breakdown", "workflow design", "coordination"],
            tools=[]  # Planner doesn't need external tools
        )
    
    async def execute(self, task: str, context: str, tool_registry) -> AgentResult:
        """Plan and break down a complex task"""
        try:
            # Validate task first
            validation = self.validate_task(task)
            if not validation["is_clear"] or not validation["is_complete"]:
                questions = self.generate_clarifying_questions(task)
                return AgentResult(
                    success=False,
                    output="Task needs clarification before planning can begin.",
                    metadata={
                        "validation": validation,
                        "clarifying_questions": questions,
                        "task_status": "needs_clarification"
                    },
                    confidence=0.3
                )
            
            # Generate task plan using OpenAI
            plan = await self._generate_plan(task, context)
            
            # Parse the plan into structured format
            structured_plan = self._parse_plan(plan)
            
            result = AgentResult(
                success=True,
                output=plan,
                metadata={
                    "structured_plan": structured_plan,
                    "task_breakdown": structured_plan.get("steps", []),
                    "estimated_duration": structured_plan.get("estimated_duration", "unknown"),
                    "required_agents": structured_plan.get("required_agents", []),
                    "dependencies": structured_plan.get("dependencies", []),
                    "validation": validation
                },
                confidence=0.9
            )
            
            # Add to history
            self.add_to_history(task, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Planner agent execution failed: {str(e)}")
            return AgentResult(
                success=False,
                output=f"Planning failed: {str(e)}",
                errors=[str(e)],
                confidence=0.1
            )
    
    async def _generate_plan(self, task: str, context: str) -> str:
        """Generate a detailed plan using OpenAI"""
        prompt = f"""
        Task: {task}
        
        Available Context:
        {context if context else "No specific context provided"}
        
        Available Agents:
        - Research Agent: Gathers and analyzes information from knowledge base
        - Data Analyst: Processes data and generates insights
        - Content Creator: Creates reports, charts, and presentations
        - Task Coordinator: Coordinates between agents and ensures completion
        
        Please create a detailed execution plan that includes:
        
        1. Task Analysis: Break down the main task into clear subtasks
        2. Agent Assignment: Which agents should handle which subtasks
        3. Execution Order: The sequence of operations
        4. Dependencies: What needs to be completed before other tasks
        5. Expected Outputs: What each agent should produce
        6. Estimated Duration: Rough time estimate for completion
        7. Success Criteria: How to measure if the task is complete
        
        Format your response as a structured plan with clear sections.
        Be specific about what each agent should do and what tools they might need.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert task planner that breaks down complex business requests into executable plans. Be thorough and specific."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI call failed: {str(e)}")
            # Fallback to template-based planning
            return self._generate_fallback_plan(task)
    
    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse the plan text into structured format"""
        try:
            # Try to extract structured information from the plan
            structured = {
                "steps": [],
                "required_agents": [],
                "estimated_duration": "unknown",
                "dependencies": [],
                "success_criteria": []
            }
            
            lines = plan_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if any(keyword in line.lower() for keyword in ["step", "agent", "duration", "dependency", "criteria"]):
                    if "step" in line.lower():
                        current_section = "steps"
                    elif "agent" in line.lower():
                        current_section = "agents"
                    elif "duration" in line.lower():
                        current_section = "duration"
                    elif "dependency" in line.lower():
                        current_section = "dependencies"
                    elif "criteria" in line.lower():
                        current_section = "criteria"
                
                # Extract content based on section
                if current_section == "steps" and line and not line.lower().startswith(("step", "agent", "duration", "dependency", "criteria")):
                    if len(line) > 10:  # Only add substantial lines
                        structured["steps"].append(line)
                
                elif current_section == "agents" and line and not line.lower().startswith(("step", "agent", "duration", "dependency", "criteria")):
                    if any(agent in line.lower() for agent in ["research", "analyst", "creator", "coordinator"]):
                        structured["required_agents"].append(line)
                
                elif current_section == "duration" and line and not line.lower().startswith(("step", "agent", "duration", "dependency", "criteria")):
                    if any(time_unit in line.lower() for time_unit in ["minute", "hour", "day", "week"]):
                        structured["estimated_duration"] = line
            
            return structured
            
        except Exception as e:
            logger.error(f"Plan parsing failed: {str(e)}")
            return {
                "steps": ["Execute the task using available agents"],
                "required_agents": ["Research Agent", "Data Analyst"],
                "estimated_duration": "unknown",
                "dependencies": [],
                "success_criteria": ["Task completion"]
            }
    
    def _generate_fallback_plan(self, task: str) -> str:
        """Generate a basic plan when OpenAI is unavailable"""
        task_lower = task.lower()
        
        if "chart" in task_lower or "visualize" in task_lower:
            return """
            Task Breakdown:
            
            Step 1: Research Agent - Gather relevant data and information
            Step 2: Data Analyst - Process and analyze the data
            Step 3: Content Creator - Create the requested chart or visualization
            Step 4: Task Coordinator - Ensure all components are properly integrated
            
            Required Agents: Research Agent, Data Analyst, Content Creator, Task Coordinator
            Estimated Duration: 15-30 minutes
            Dependencies: Each step depends on the completion of the previous step
            Success Criteria: Chart/visualization created and presented to user
            """
        
        elif "analyze" in task_lower or "research" in task_lower:
            return """
            Task Breakdown:
            
            Step 1: Research Agent - Gather comprehensive information from knowledge base
            Step 2: Data Analyst - Analyze patterns and extract insights
            Step 3: Content Creator - Format findings into a clear report
            Step 4: Task Coordinator - Review and finalize the analysis
            
            Required Agents: Research Agent, Data Analyst, Content Creator, Task Coordinator
            Estimated Duration: 20-45 minutes
            Dependencies: Analysis depends on research completion
            Success Criteria: Comprehensive analysis report delivered
            """
        
        else:
            return """
            Task Breakdown:
            
            Step 1: Research Agent - Understand the task requirements and gather context
            Step 2: Data Analyst - Process any relevant data
            Step 3: Content Creator - Generate the requested output
            Step 4: Task Coordinator - Ensure quality and completion
            
            Required Agents: Research Agent, Data Analyst, Content Creator, Task Coordinator
            Estimated Duration: 15-40 minutes
            Dependencies: Sequential execution with coordination
            Success Criteria: Task completed according to requirements
            """
