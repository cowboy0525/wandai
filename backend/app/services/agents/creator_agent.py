import openai
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class CreatorAgent(BaseAgent):
    """Agent responsible for creating reports, charts, and presentations"""
    
    def __init__(self):
        super().__init__(
            name="Content Creator",
            role="Creates reports, charts, and presentations based on data and insights",
            capabilities=["content creation", "visualization", "report writing", "presentation design"],
            tools=["chart_creator", "code_executor"]
        )
    
    async def execute(self, task: str, context: str, tool_registry) -> AgentResult:
        """Create content based on the task and context"""
        try:
            # Validate task
            validation = self.validate_task(task)
            if not validation["is_clear"]:
                questions = self.generate_clarifying_questions(task)
                return AgentResult(
                    success=False,
                    output="Content creation task needs clarification.",
                    metadata={"validation": validation, "clarifying_questions": questions},
                    confidence=0.3
                )
            
            # Determine content type
            content_type = self._determine_content_type(task)
            
            # Create content
            content = await self._create_content(task, context, content_type, tool_registry)
            
            # Format output
            formatted_output = self._format_output(content, content_type)
            
            result = AgentResult(
                success=True,
                output=formatted_output,
                metadata={
                    "content_type": content_type,
                    "content_details": content,
                    "creation_method": "ai_generated",
                    "format": "structured_report"
                },
                confidence=0.8,
                tools_used=["content_engine", "formatting_engine"]
            )
            
            self.add_to_history(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Creator agent execution failed: {str(e)}")
            return AgentResult(
                success=False,
                output=f"Content creation failed: {str(e)}",
                errors=[str(e)],
                confidence=0.1
            )
    
    def _determine_content_type(self, task: str) -> str:
        """Determine what type of content to create"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["chart", "graph", "visualization", "plot"]):
            return "chart"
        elif any(word in task_lower for word in ["report", "summary", "analysis"]):
            return "report"
        elif any(word in task_lower for word in ["presentation", "slide", "deck"]):
            return "presentation"
        elif any(word in task_lower for word in ["document", "memo", "brief"]):
            return "document"
        else:
            return "report"  # Default to report
    
    async def _create_content(self, task: str, context: str, content_type: str, tool_registry) -> Dict[str, Any]:
        """Create the actual content"""
        content = {}
        
        try:
            if content_type == "chart":
                content["chart"] = await self._create_chart(task, context, tool_registry)
            
            if content_type in ["report", "document"]:
                content["text"] = await self._create_report(task, context)
            
            if content_type == "presentation":
                content["slides"] = await self._create_presentation(task, context)
            
            # Add metadata
            content["metadata"] = {
                "task": task,
                "content_type": content_type,
                "created_at": "now",
                "source_context": context[:200] + "..." if len(context) > 200 else context
            }
            
        except Exception as e:
            logger.error(f"Content creation failed: {str(e)}")
            content["error"] = str(e)
        
        return content
    
    async def _create_chart(self, task: str, context: str, tool_registry) -> Dict[str, Any]:
        """Create a chart using the chart creation tool"""
        try:
            # Extract chart requirements from task
            chart_type = self._extract_chart_type(task)
            chart_data = self._extract_chart_data(context)
            chart_title = self._extract_chart_title(task)
            
            if tool_registry.tool_exists("chart_creator"):
                chart_result = await tool_registry.execute_tool("chart_creator", {
                    "type": chart_type,
                    "data": chart_data,
                    "title": chart_title
                })
                
                if chart_result["success"]:
                    return {
                        "type": chart_type,
                        "title": chart_title,
                        "data": chart_data,
                        "image_base64": chart_result.get("image_base64"),
                        "message": chart_result["message"]
                    }
            
            # Fallback chart creation
            return self._create_fallback_chart(chart_type, chart_data, chart_title)
            
        except Exception as e:
            logger.error(f"Chart creation failed: {str(e)}")
            return {"error": f"Chart creation failed: {str(e)}"}
    
    def _extract_chart_type(self, task: str) -> str:
        """Extract chart type from task description"""
        task_lower = task.lower()
        
        if "line" in task_lower:
            return "line"
        elif "bar" in task_lower:
            return "bar"
        elif "pie" in task_lower:
            return "pie"
        elif "scatter" in task_lower:
            return "scatter"
        else:
            return "line"  # Default to line chart
    
    def _extract_chart_data(self, context: str) -> Dict[str, Any]:
        """Extract chart data from context"""
        try:
            import re
            
            # Look for data patterns in context
            numbers = re.findall(r'\d+\.?\d*', context)
            
            if len(numbers) >= 4:
                # Assume quarterly data
                quarters = ["Q1", "Q2", "Q3", "Q4"]
                values = [float(num) for num in numbers[:4]]
                
                return {
                    "x": quarters,
                    "y": values
                }
            elif len(numbers) >= 2:
                # Simple data
                labels = [f"Item {i+1}" for i in range(len(numbers))]
                values = [float(num) for num in numbers]
                
                return {
                    "x": labels,
                    "y": values
                }
            else:
                # Sample data
                return {
                    "x": ["Jan", "Feb", "Mar", "Apr"],
                    "y": [100, 120, 140, 160]
                }
                
        except:
            return {
                "x": ["Sample 1", "Sample 2", "Sample 3"],
                "y": [10, 20, 30]
            }
    
    def _extract_chart_title(self, task: str) -> str:
        """Extract chart title from task"""
        # Remove common words and clean up
        title = task.replace("create", "").replace("make", "").replace("generate", "").strip()
        if title:
            return title[:50]  # Limit length
        return "Generated Chart"
    
    def _create_fallback_chart(self, chart_type: str, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a fallback chart when tool is unavailable"""
        return {
            "type": chart_type,
            "title": title,
            "data": data,
            "message": f"Chart specification created for {chart_type} chart",
            "fallback": True
        }
    
    async def _create_report(self, task: str, context: str) -> str:
        """Create a text report using OpenAI"""
        try:
            prompt = f"""
            Task: {task}
            
            Context: {context}
            
            Please create a comprehensive report that includes:
            
            1. Executive Summary
            2. Key Findings
            3. Detailed Analysis
            4. Recommendations
            5. Conclusion
            
            Make the report professional, clear, and actionable.
            Use the context provided to inform the content.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional business writer that creates clear, actionable reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Report creation failed: {str(e)}")
            return f"Report creation failed: {str(e)}. Please try again later."
    
    async def _create_presentation(self, task: str, context: str) -> List[Dict[str, Any]]:
        """Create presentation slides using OpenAI"""
        try:
            prompt = f"""
            Task: {task}
            
            Context: {context}
            
            Please create a presentation outline with 5-7 slides including:
            
            1. Title Slide
            2. Agenda/Overview
            3. Key Points (2-3 slides)
            4. Analysis/Findings
            5. Recommendations
            6. Conclusion
            
            For each slide, provide:
            - Slide title
            - Key bullet points
            - Suggested visual elements
            
            Format as a structured outline.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a presentation designer that creates clear, engaging slide outlines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            # Parse the response into slide structure
            slides = self._parse_presentation_outline(response.choices[0].message.content.strip())
            return slides
            
        except Exception as e:
            logger.error(f"Presentation creation failed: {str(e)}")
            return [{"title": "Error", "content": f"Presentation creation failed: {str(e)}"}]
    
    def _parse_presentation_outline(self, outline: str) -> List[Dict[str, Any]]:
        """Parse presentation outline into structured slides"""
        try:
            lines = outline.split('\n')
            slides = []
            current_slide = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect slide headers
                if any(keyword in line.lower() for keyword in ["slide", "title", "agenda", "conclusion"]):
                    if current_slide:
                        slides.append(current_slide)
                    
                    current_slide = {
                        "title": line,
                        "content": [],
                        "visual_elements": []
                    }
                
                # Add content to current slide
                elif current_slide and line.startswith('-'):
                    current_slide["content"].append(line[1:].strip())
                elif current_slide and line:
                    current_slide["content"].append(line)
            
            # Add the last slide
            if current_slide:
                slides.append(current_slide)
            
            return slides if slides else [{"title": "Presentation", "content": ["Content creation completed"]}]
            
        except Exception as e:
            logger.error(f"Presentation parsing failed: {str(e)}")
            return [{"title": "Presentation", "content": ["Content creation completed"]}]
    
    def _format_output(self, content: Dict[str, Any], content_type: str) -> str:
        """Format the content into a readable output"""
        try:
            if content_type == "chart":
                return f"Chart Created: {content.get('chart', {}).get('title', 'Unknown')}\n{content.get('chart', {}).get('message', 'Chart generation completed')}"
            
            elif content_type == "report":
                return content.get('text', 'Report creation completed')
            
            elif content_type == "presentation":
                slides = content.get('slides', [])
                output = "Presentation Created:\n\n"
                for i, slide in enumerate(slides, 1):
                    output += f"Slide {i}: {slide.get('title', 'Untitled')}\n"
                    for point in slide.get('content', [])[:3]:  # Limit to 3 points per slide
                        output += f"  • {point}\n"
                    output += "\n"
                return output
            
            else:
                return "Content creation completed successfully"
                
        except Exception as e:
            logger.error(f"Output formatting failed: {str(e)}")
            return "Content creation completed but formatting failed"
