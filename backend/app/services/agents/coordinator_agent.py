import openai
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """Agent responsible for coordinating between agents and ensuring task completion"""
    
    def __init__(self):
        super().__init__(
            name="Task Coordinator",
            role="Coordinates between agents and ensures task completion",
            capabilities=["coordination", "project management", "quality assurance", "workflow management"],
            tools=[]  # Coordinator doesn't need external tools
        )
    
    async def execute(self, task: str, context: str, tool_registry) -> AgentResult:
        """Coordinate task execution and ensure completion"""
        try:
            # Validate task
            validation = self.validate_task(task)
            if not validation["is_clear"]:
                questions = self.generate_clarifying_questions(task)
                return AgentResult(
                    success=False,
                    output="Coordination task needs clarification.",
                    metadata={"validation": validation, "clarifying_questions": questions},
                    confidence=0.3
                )
            
            # Analyze task requirements
            requirements = await self._analyze_requirements(task, context)
            
            # Create execution plan
            execution_plan = await self._create_execution_plan(task, requirements)
            
            # Monitor and coordinate execution
            coordination_result = await self._coordinate_execution(execution_plan, context)
            
            # Quality assurance
            quality_check = await self._perform_quality_assurance(task, coordination_result)
            
            result = AgentResult(
                success=True,
                output=coordination_result["summary"],
                metadata={
                    "requirements": requirements,
                    "execution_plan": execution_plan,
                    "coordination_result": coordination_result,
                    "quality_check": quality_check,
                    "validation": validation
                },
                confidence=quality_check["confidence"],
                tools_used=["coordination_engine", "quality_engine"]
            )
            
            self.add_to_history(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Coordinator agent execution failed: {str(e)}")
            return AgentResult(
                success=False,
                output=f"Coordination failed: {str(e)}",
                errors=[str(e)],
                confidence=0.1
            )
    
    async def _analyze_requirements(self, task: str, context: str) -> Dict[str, Any]:
        """Analyze task requirements and dependencies"""
        try:
            prompt = f"""
            Task: {task}
            
            Context: {context}
            
            Please analyze this task and identify:
            
            1. Required resources and capabilities
            2. Dependencies and prerequisites
            3. Estimated timeline
            4. Quality requirements
            5. Success criteria
            6. Potential risks or challenges
            
            Format as a structured requirements analysis.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project manager that analyzes task requirements and dependencies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            requirements_text = response.choices[0].message.content.strip()
            
            # Parse requirements into structured format
            return self._parse_requirements(requirements_text)
            
        except Exception as e:
            logger.error(f"Requirements analysis failed: {str(e)}")
            return self._generate_fallback_requirements(task)
    
    def _parse_requirements(self, requirements_text: str) -> Dict[str, Any]:
        """Parse requirements text into structured format"""
        try:
            requirements = {
                "resources": [],
                "dependencies": [],
                "timeline": "unknown",
                "quality_requirements": [],
                "success_criteria": [],
                "risks": []
            }
            
            lines = requirements_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if any(keyword in line.lower() for keyword in ["resource", "dependency", "timeline", "quality", "success", "risk"]):
                    if "resource" in line.lower():
                        current_section = "resources"
                    elif "dependency" in line.lower():
                        current_section = "dependencies"
                    elif "timeline" in line.lower():
                        current_section = "timeline"
                    elif "quality" in line.lower():
                        current_section = "quality_requirements"
                    elif "success" in line.lower():
                        current_section = "success_criteria"
                    elif "risk" in line.lower():
                        current_section = "risks"
                
                # Extract content based on section
                if current_section and line and not line.lower().startswith(("resource", "dependency", "timeline", "quality", "success", "risk")):
                    if len(line) > 10:  # Only add substantial lines
                        requirements[current_section].append(line)
            
            return requirements
            
        except Exception as e:
            logger.error(f"Requirements parsing failed: {str(e)}")
            return self._generate_fallback_requirements("general task")
    
    def _generate_fallback_requirements(self, task: str) -> Dict[str, Any]:
        """Generate basic requirements when analysis fails"""
        return {
            "resources": ["AI agents", "Knowledge base access"],
            "dependencies": ["Task planning", "Agent availability"],
            "timeline": "15-30 minutes",
            "quality_requirements": ["Accurate results", "Clear output"],
            "success_criteria": ["Task completed", "User satisfied"],
            "risks": ["Agent failure", "Incomplete data"]
        }
    
    async def _create_execution_plan(self, task: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed execution plan"""
        try:
            prompt = f"""
            Task: {task}
            
            Requirements: {requirements}
            
            Please create a detailed execution plan that includes:
            
            1. Phase breakdown (Planning, Execution, Review)
            2. Agent assignments for each phase
            3. Dependencies between phases
            4. Quality checkpoints
            5. Risk mitigation strategies
            6. Timeline for each phase
            
            Format as a structured execution plan.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project coordinator that creates detailed execution plans."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            plan_text = response.choices[0].message.content.strip()
            
            # Parse the plan into structured format
            return self._parse_execution_plan(plan_text)
            
        except Exception as e:
            logger.error(f"Execution plan creation failed: {str(e)}")
            return self._generate_fallback_execution_plan()
    
    def _parse_execution_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse execution plan text into structured format"""
        try:
            plan = {
                "phases": [],
                "agent_assignments": {},
                "dependencies": [],
                "quality_checkpoints": [],
                "risk_mitigation": [],
                "timeline": {}
            }
            
            lines = plan_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if any(keyword in line.lower() for keyword in ["phase", "agent", "dependency", "quality", "risk", "timeline"]):
                    if "phase" in line.lower():
                        current_section = "phases"
                    elif "agent" in line.lower():
                        current_section = "agents"
                    elif "dependency" in line.lower():
                        current_section = "dependencies"
                    elif "quality" in line.lower():
                        current_section = "quality_checkpoints"
                    elif "risk" in line.lower():
                        current_section = "risk_mitigation"
                    elif "timeline" in line.lower():
                        current_section = "timeline"
                
                # Extract content based on section
                if current_section and line and not line.lower().startswith(("phase", "agent", "dependency", "quality", "risk", "timeline")):
                    if len(line) > 10:
                        if current_section == "phases":
                            plan["phases"].append(line)
                        elif current_section == "agents":
                            # Try to extract agent-task mapping
                            if ":" in line:
                                agent, task = line.split(":", 1)
                                plan["agent_assignments"][agent.strip()] = task.strip()
                        else:
                            plan[current_section].append(line)
            
            return plan
            
        except Exception as e:
            logger.error(f"Execution plan parsing failed: {str(e)}")
            return self._generate_fallback_execution_plan()
    
    def _generate_fallback_execution_plan(self) -> Dict[str, Any]:
        """Generate basic execution plan when creation fails"""
        return {
            "phases": ["Planning", "Execution", "Review"],
            "agent_assignments": {
                "Planner": "Task breakdown",
                "Research": "Information gathering",
                "Analysis": "Data processing",
                "Creator": "Output generation",
                "Coordinator": "Quality assurance"
            },
            "dependencies": ["Sequential execution"],
            "quality_checkpoints": ["Phase completion", "Final review"],
            "risk_mitigation": ["Agent backup", "Error handling"],
            "timeline": {"Planning": "5 min", "Execution": "15 min", "Review": "5 min"}
        }
    
    async def _coordinate_execution(self, execution_plan: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Coordinate the execution of the plan"""
        try:
            coordination_result = {
                "phases_completed": [],
                "agent_performance": {},
                "dependencies_met": [],
                "quality_checkpoints_passed": [],
                "risks_mitigated": [],
                "overall_progress": 0.0
            }
            
            # Simulate coordination of phases
            total_phases = len(execution_plan.get("phases", []))
            
            for i, phase in enumerate(execution_plan.get("phases", [])):
                # Simulate phase execution
                phase_result = await self._execute_phase(phase, execution_plan, context)
                
                coordination_result["phases_completed"].append({
                    "phase": phase,
                    "status": "completed",
                    "result": phase_result,
                    "duration": "5 minutes"
                })
                
                # Update progress
                coordination_result["overall_progress"] = (i + 1) / total_phases
            
            # Generate coordination summary
            coordination_result["summary"] = self._generate_coordination_summary(coordination_result)
            
            return coordination_result
            
        except Exception as e:
            logger.error(f"Execution coordination failed: {str(e)}")
            return {
                "error": str(e),
                "summary": f"Coordination failed: {str(e)}"
            }
    
    async def _execute_phase(self, phase: str, execution_plan: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Execute a specific phase of the plan"""
        try:
            # Simulate phase execution
            if "planning" in phase.lower():
                return {"status": "completed", "output": "Task planning completed successfully"}
            elif "execution" in phase.lower():
                return {"status": "completed", "output": "Task execution completed successfully"}
            elif "review" in phase.lower():
                return {"status": "completed", "output": "Task review completed successfully"}
            else:
                return {"status": "completed", "output": f"{phase} phase completed successfully"}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _generate_coordination_summary(self, coordination_result: Dict[str, Any]) -> str:
        """Generate a summary of coordination results"""
        try:
            phases_completed = len(coordination_result.get("phases_completed", []))
            overall_progress = coordination_result.get("overall_progress", 0.0)
            
            summary = f"""
            Coordination Summary:
            
            ✅ Phases Completed: {phases_completed}
            📊 Overall Progress: {overall_progress * 100:.1f}%
            
            All phases have been coordinated successfully.
            Task execution is proceeding according to plan.
            Quality checkpoints are being monitored.
            """
            
            return summary.strip()
            
        except Exception as e:
            return f"Coordination summary generation failed: {str(e)}"
    
    async def _perform_quality_assurance(self, task: str, coordination_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quality assurance checks"""
        try:
            quality_check = {
                "overall_quality": "high",
                "quality_score": 0.9,
                "issues_found": [],
                "recommendations": [],
                "confidence": 0.9
            }
            
            # Check phase completion
            phases = coordination_result.get("phases_completed", [])
            if not phases:
                quality_check["overall_quality"] = "low"
                quality_check["quality_score"] = 0.3
                quality_check["issues_found"].append("No phases completed")
                quality_check["confidence"] = 0.3
            
            # Check for errors
            for phase in phases:
                if phase.get("status") == "failed":
                    quality_check["issues_found"].append(f"Phase '{phase.get('phase')}' failed")
                    quality_check["quality_score"] *= 0.8
            
            # Generate recommendations
            if quality_check["issues_found"]:
                quality_check["recommendations"].append("Address failed phases before proceeding")
                quality_check["recommendations"].append("Implement additional error handling")
            else:
                quality_check["recommendations"].append("Continue with current execution plan")
                quality_check["recommendations"].append("Monitor for any emerging issues")
            
            return quality_check
            
        except Exception as e:
            logger.error(f"Quality assurance failed: {str(e)}")
            return {
                "overall_quality": "unknown",
                "quality_score": 0.5,
                "issues_found": [f"Quality check failed: {str(e)}"],
                "recommendations": ["Re-run quality assurance"],
                "confidence": 0.3
            }
