import openai
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """Agent responsible for gathering and analyzing information"""
    
    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="Gathers and analyzes information from the knowledge base and external sources",
            capabilities=["research", "information gathering", "data collection", "context analysis"],
            tools=["api_client"]  # Can use API calls for external research
        )
    
    async def execute(self, task: str, context: str, tool_registry) -> AgentResult:
        """Conduct research and gather information"""
        try:
            # Validate task
            validation = self.validate_task(task)
            if not validation["is_clear"]:
                questions = self.generate_clarifying_questions(task)
                return AgentResult(
                    success=False,
                    output="Research task needs clarification.",
                    metadata={
                        "validation": validation,
                        "clarifying_questions": questions
                    },
                    confidence=0.3
                )
            
            # Conduct research
            research_results = await self._conduct_research(task, context, tool_registry)
            
            # Analyze findings
            analysis = await self._analyze_findings(task, research_results)
            
            result = AgentResult(
                success=True,
                output=analysis["summary"],
                metadata={
                    "research_findings": research_results,
                    "key_insights": analysis["insights"],
                    "data_sources": analysis["sources"],
                    "confidence_level": analysis["confidence"],
                    "validation": validation
                },
                confidence=analysis["confidence"],
                tools_used=["research_engine", "analysis_engine"]
            )
            
            self.add_to_history(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Research agent execution failed: {str(e)}")
            return AgentResult(
                success=False,
                output=f"Research failed: {str(e)}",
                errors=[str(e)],
                confidence=0.1
            )
    
    async def _conduct_research(self, task: str, context: str, tool_registry) -> Dict[str, Any]:
        """Conduct comprehensive research on the task"""
        research_results = {
            "knowledge_base_findings": [],
            "external_findings": [],
            "context_analysis": "",
            "gaps_identified": []
        }
        
        # Analyze provided context
        if context:
            research_results["context_analysis"] = await self._analyze_context(context)
        
        # Identify research areas
        research_areas = self._identify_research_areas(task)
        
        # Research each area
        for area in research_areas:
            findings = await self._research_area(area, tool_registry)
            research_results["knowledge_base_findings"].extend(findings)
        
        # Identify knowledge gaps
        research_results["gaps_identified"] = self._identify_knowledge_gaps(task, research_results)
        
        return research_results
    
    async def _analyze_context(self, context: str) -> str:
        """Analyze the provided context for relevance and completeness"""
        try:
            prompt = f"""
            Context: {context}
            
            Please analyze this context and provide:
            1. Key topics and themes
            2. Relevance to research tasks
            3. Completeness assessment
            4. Any missing information
            
            Format as a concise analysis.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a research analyst that evaluates context relevance and completeness."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Context analysis failed: {str(e)}")
            return f"Context analysis: {context[:200]}... (analysis failed)"
    
    def _identify_research_areas(self, task: str) -> List[str]:
        """Identify specific areas to research based on the task"""
        task_lower = task.lower()
        research_areas = []
        
        # Financial analysis
        if any(word in task_lower for word in ["financial", "revenue", "profit", "cost", "quarter"]):
            research_areas.extend([
                "financial performance metrics",
                "quarterly reports",
                "trend analysis",
                "comparative data"
            ])
        
        # Market analysis
        if any(word in task_lower for word in ["market", "trend", "competition", "industry"]):
            research_areas.extend([
                "market trends",
                "competitive analysis",
                "industry reports",
                "market size data"
            ])
        
        # Customer analysis
        if any(word in task_lower for word in ["customer", "user", "feedback", "satisfaction"]):
            research_areas.extend([
                "customer feedback",
                "user behavior data",
                "satisfaction metrics",
                "customer segments"
            ])
        
        # Product analysis
        if any(word in task_lower for word in ["product", "feature", "performance", "quality"]):
            research_areas.extend([
                "product specifications",
                "performance metrics",
                "feature comparisons",
                "quality assessments"
            ])
        
        # If no specific areas identified, use general research
        if not research_areas:
            research_areas = ["general information", "relevant data", "context details"]
        
        return research_areas
    
    async def _research_area(self, area: str, tool_registry) -> List[Dict[str, Any]]:
        """Research a specific area and return findings"""
        findings = []
        
        try:
            # Simulate research findings
            if "financial" in area.lower():
                findings.append({
                    "type": "financial_data",
                    "content": "Financial performance metrics and trends",
                    "relevance": "high",
                    "source": "knowledge_base"
                })
            
            elif "market" in area.lower():
                findings.append({
                    "type": "market_data",
                    "content": "Market trends and competitive landscape",
                    "relevance": "high",
                    "source": "knowledge_base"
                })
            
            elif "customer" in area.lower():
                findings.append({
                    "type": "customer_data",
                    "content": "Customer feedback and satisfaction metrics",
                    "relevance": "medium",
                    "source": "knowledge_base"
                })
            
            else:
                findings.append({
                    "type": "general_info",
                    "content": f"General information about {area}",
                    "relevance": "medium",
                    "source": "knowledge_base"
                })
            
        except Exception as e:
            logger.error(f"Research area {area} failed: {str(e)}")
            findings.append({
                "type": "error",
                "content": f"Research failed for {area}: {str(e)}",
                "relevance": "low",
                "source": "error"
            })
        
        return findings
    
    def _identify_knowledge_gaps(self, task: str, research_results: Dict[str, Any]) -> List[str]:
        """Identify gaps in the current knowledge base"""
        gaps = []
        task_lower = task.lower()
        
        # Check for missing financial data
        if any(word in task_lower for word in ["financial", "revenue", "profit"]):
            if not any("financial" in str(finding) for finding in research_results["knowledge_base_findings"]):
                gaps.append("Financial performance data")
        
        # Check for missing market data
        if any(word in task_lower for word in ["market", "trend", "competition"]):
            if not any("market" in str(finding) for finding in research_results["knowledge_base_findings"]):
                gaps.append("Market trend data")
        
        # Check for missing customer data
        if any(word in task_lower for word in ["customer", "user", "feedback"]):
            if not any("customer" in str(finding) for finding in research_results["knowledge_base_findings"]):
                gaps.append("Customer feedback data")
        
        # Check for missing temporal data
        if any(word in task_lower for word in ["trend", "quarter", "period"]):
            gaps.append("Historical trend data")
        
        return gaps
    
    async def _analyze_findings(self, task: str, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze research findings and generate insights"""
        try:
            # Prepare findings summary
            findings_text = "\n".join([
                f"- {finding['type']}: {finding['content']}"
                for finding in research_results["knowledge_base_findings"]
            ])
            
            gaps_text = "\n".join([f"- {gap}" for gap in research_results["gaps_identified"]])
            
            prompt = f"""
            Task: {task}
            
            Research Findings:
            {findings_text}
            
            Knowledge Gaps:
            {gaps_text}
            
            Context Analysis:
            {research_results.get('context_analysis', 'No context provided')}
            
            Please provide:
            1. A comprehensive summary of findings
            2. Key insights relevant to the task
            3. Assessment of data completeness
            4. Confidence level in the findings (0-100%)
            5. Recommendations for addressing gaps
            
            Format as a clear, structured analysis.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research analyst that synthesizes findings into actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract confidence level
            confidence = self._extract_confidence(analysis_text)
            
            return {
                "summary": analysis_text,
                "insights": self._extract_insights(analysis_text),
                "sources": [f["source"] for f in research_results["knowledge_base_findings"]],
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Findings analysis failed: {str(e)}")
            return {
                "summary": f"Research completed but analysis failed: {str(e)}",
                "insights": ["Research data available but needs manual analysis"],
                "sources": ["knowledge_base"],
                "confidence": 0.5
            }
    
    def _extract_confidence(self, analysis_text: str) -> float:
        """Extract confidence level from analysis text"""
        try:
            # Look for confidence indicators
            if "high confidence" in analysis_text.lower() or "very confident" in analysis_text.lower():
                return 0.9
            elif "medium confidence" in analysis_text.lower() or "moderately confident" in analysis_text.lower():
                return 0.7
            elif "low confidence" in analysis_text.lower() or "uncertain" in analysis_text.lower():
                return 0.3
            else:
                return 0.6  # Default confidence
        except:
            return 0.6
    
    def _extract_insights(self, analysis_text: str) -> List[str]:
        """Extract key insights from analysis text"""
        try:
            lines = analysis_text.split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                if line and any(keyword in line.lower() for keyword in ["insight", "finding", "key", "important", "notable"]):
                    insights.append(line)
            
            return insights[:5]  # Limit to top 5 insights
        except:
            return ["Analysis completed successfully"]
