import openai
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class AnalysisAgent(BaseAgent):
    """Agent responsible for data analysis and insights generation"""
    
    def __init__(self):
        super().__init__(
            name="Data Analyst",
            role="Processes data and generates insights using analytical tools",
            capabilities=["data analysis", "statistical analysis", "trend detection", "insight generation"],
            tools=["data_analyzer", "code_executor"]
        )
    
    async def execute(self, task: str, context: str, tool_registry) -> AgentResult:
        """Analyze data and generate insights"""
        try:
            # Validate task
            validation = self.validate_task(task)
            if not validation["is_clear"]:
                questions = self.generate_clarifying_questions(task)
                return AgentResult(
                    success=False,
                    output="Analysis task needs clarification.",
                    metadata={"validation": validation, "clarifying_questions": questions},
                    confidence=0.3
                )
            
            # Extract data from context
            data = self._extract_data_from_context(context)
            
            # Perform analysis
            analysis_results = await self._perform_analysis(task, data, tool_registry)
            
            # Generate insights
            insights = await self._generate_insights(task, analysis_results)
            
            result = AgentResult(
                success=True,
                output=insights["summary"],
                metadata={
                    "analysis_results": analysis_results,
                    "key_insights": insights["insights"],
                    "data_processed": len(data) if data else 0,
                    "analysis_methods": insights["methods"],
                    "confidence_level": insights["confidence"]
                },
                confidence=insights["confidence"],
                tools_used=["data_analyzer", "analysis_engine"]
            )
            
            self.add_to_history(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Analysis agent execution failed: {str(e)}")
            return AgentResult(
                success=False,
                output=f"Analysis failed: {str(e)}",
                errors=[str(e)],
                confidence=0.1
            )
    
    def _extract_data_from_context(self, context: str) -> List[Any]:
        """Extract numerical data from context for analysis"""
        try:
            # Simple data extraction - in production, use more sophisticated parsing
            import re
            
            # Look for numbers in the context
            numbers = re.findall(r'\d+\.?\d*', context)
            
            # Convert to appropriate data types
            data = []
            for num in numbers:
                try:
                    if '.' in num:
                        data.append(float(num))
                    else:
                        data.append(int(num))
                except:
                    continue
            
            return data
        except:
            return []
    
    async def _perform_analysis(self, task: str, data: List[Any], tool_registry) -> Dict[str, Any]:
        """Perform various types of analysis on the data"""
        analysis_results = {}
        
        if not data:
            return {"error": "No data available for analysis"}
        
        try:
            # Basic statistical analysis
            if tool_registry.tool_exists("data_analyzer"):
                basic_analysis = await tool_registry.execute_tool("data_analyzer", {
                    "data": data,
                    "type": "basic"
                })
                analysis_results["basic_stats"] = basic_analysis
            
            # Trend analysis
            if len(data) > 1:
                trend_analysis = await tool_registry.execute_tool("data_analyzer", {
                    "data": data,
                    "type": "trend"
                })
                analysis_results["trend_analysis"] = trend_analysis
            
            # Custom analysis based on task
            custom_analysis = await self._custom_analysis(task, data)
            analysis_results["custom_analysis"] = custom_analysis
            
        except Exception as e:
            logger.error(f"Analysis execution failed: {str(e)}")
            analysis_results["error"] = str(e)
        
        return analysis_results
    
    async def _custom_analysis(self, task: str, data: List[Any]) -> Dict[str, Any]:
        """Perform custom analysis based on the specific task"""
        task_lower = task.lower()
        
        if "financial" in task_lower or "revenue" in task_lower:
            return self._financial_analysis(data)
        elif "trend" in task_lower or "growth" in task_lower:
            return self._trend_analysis(data)
        elif "performance" in task_lower or "efficiency" in task_lower:
            return self._performance_analysis(data)
        else:
            return self._general_analysis(data)
    
    def _financial_analysis(self, data: List[Any]) -> Dict[str, Any]:
        """Perform financial-specific analysis"""
        if not data:
            return {"error": "No financial data available"}
        
        try:
            # Calculate financial metrics
            total = sum(data)
            avg = total / len(data)
            growth_rate = ((data[-1] - data[0]) / data[0] * 100) if data[0] != 0 else 0
            
            return {
                "total_value": total,
                "average_value": avg,
                "growth_rate": f"{growth_rate:.2f}%",
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable",
                "volatility": self._calculate_volatility(data)
            }
        except Exception as e:
            return {"error": f"Financial analysis failed: {str(e)}"}
    
    def _trend_analysis(self, data: List[Any]) -> Dict[str, Any]:
        """Perform trend-specific analysis"""
        if len(data) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        try:
            # Linear trend calculation
            n = len(data)
            x_values = list(range(n))
            
            # Simple linear regression
            sum_x = sum(x_values)
            sum_y = sum(data)
            sum_xy = sum(x * y for x, y in zip(x_values, data))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict next value
            next_value = slope * n + intercept
            
            return {
                "trend_direction": "upward" if slope > 0 else "downward" if slope < 0 else "stable",
                "trend_strength": abs(slope),
                "predicted_next": next_value,
                "confidence": min(0.9, 0.5 + abs(slope) * 10)  # Higher slope = higher confidence
            }
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def _performance_analysis(self, data: List[Any]) -> Dict[str, Any]:
        """Perform performance-specific analysis"""
        if not data:
            return {"error": "No performance data available"}
        
        try:
            # Performance metrics
            best_performance = max(data)
            worst_performance = min(data)
            performance_range = best_performance - worst_performance
            consistency = 1 - (performance_range / best_performance) if best_performance != 0 else 0
            
            return {
                "best_performance": best_performance,
                "worst_performance": worst_performance,
                "performance_range": performance_range,
                "consistency_score": consistency,
                "improvement_potential": best_performance - (sum(data) / len(data))
            }
        except Exception as e:
            return {"error": f"Performance analysis failed: {str(e)}"}
    
    def _general_analysis(self, data: List[Any]) -> Dict[str, Any]:
        """Perform general statistical analysis"""
        if not data:
            return {"error": "No data available"}
        
        try:
            return {
                "data_points": len(data),
                "mean": sum(data) / len(data),
                "median": sorted(data)[len(data) // 2],
                "min_value": min(data),
                "max_value": max(data),
                "data_range": max(data) - min(data)
            }
        except Exception as e:
            return {"error": f"General analysis failed: {str(e)}"}
    
    def _calculate_volatility(self, data: List[Any]) -> float:
        """Calculate volatility (standard deviation) of the data"""
        try:
            if len(data) < 2:
                return 0.0
            
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
            return variance ** 0.5
        except:
            return 0.0
    
    async def _generate_insights(self, task: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from analysis results"""
        try:
            # Prepare analysis summary
            analysis_text = "\n".join([
                f"- {key}: {value}"
                for key, value in analysis_results.items()
                if key != "error" and value
            ])
            
            prompt = f"""
            Task: {task}
            
            Analysis Results:
            {analysis_text}
            
            Please provide:
            1. A comprehensive summary of the analysis
            2. Key insights and findings
            3. Recommendations based on the data
            4. Confidence level in the analysis (0-100%)
            5. Any limitations or caveats
            
            Format as a clear, actionable report.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data analyst that generates insights from analysis results."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            insights_text = response.choices[0].message.content.strip()
            
            return {
                "summary": insights_text,
                "insights": self._extract_insights(insights_text),
                "methods": list(analysis_results.keys()),
                "confidence": self._extract_confidence(insights_text)
            }
            
        except Exception as e:
            logger.error(f"Insights generation failed: {str(e)}")
            return {
                "summary": f"Analysis completed but insights generation failed: {str(e)}",
                "insights": ["Data analysis completed successfully"],
                "methods": list(analysis_results.keys()),
                "confidence": 0.6
            }
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract key insights from text"""
        try:
            lines = text.split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                if line and any(keyword in line.lower() for keyword in ["insight", "finding", "key", "important", "notable"]):
                    insights.append(line)
            
            return insights[:5]
        except:
            return ["Analysis completed successfully"]
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence level from text"""
        try:
            if "high confidence" in text.lower() or "very confident" in text.lower():
                return 0.9
            elif "medium confidence" in text.lower() or "moderately confident" in text.lower():
                return 0.7
            elif "low confidence" in text.lower() or "uncertain" in text.lower():
                return 0.3
            else:
                return 0.6
        except:
            return 0.6
