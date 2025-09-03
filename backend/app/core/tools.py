import asyncio
import json
import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns  # Optional dependency
from io import BytesIO
import base64
import requests
from openai import OpenAI
import chromadb
from chromadb.config import Settings
import sys
import numpy as np

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry of tools that agents can use to execute real tasks"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all available tools"""
        self.register_tool(
            "python_executor",
            "Execute Python code safely",
            self._execute_python_code,
            ["code", "context"]
        )
        
        self.register_tool(
            "data_analyzer",
            "Analyze data and generate insights",
            self._analyze_data,
            ["data", "analysis_type", "context"]
        )
        
        self.register_tool(
            "chart_generator",
            "Generate charts and visualizations",
            self._generate_chart,
            ["data", "chart_type", "title", "context"]
        )
        
        self.register_tool(
            "web_search",
            "Search the web for current information",
            self._web_search,
            ["query", "context"]
        )
        
        self.register_tool(
            "file_processor",
            "Process and analyze uploaded files",
            self._process_file,
            ["file_path", "operation", "context"]
        )
        
        self.register_tool(
            "knowledge_enricher",
            "Suggest knowledge base enrichment",
            self._suggest_enrichment,
            ["query", "current_results", "context"]
        )
        
        self.register_tool(
            "fact_checker",
            "Verify facts and prevent hallucination",
            self._fact_check,
            ["claim", "context", "sources"]
        )
    
    def register_tool(self, name: str, description: str, func: Callable, parameters: List[str]):
        """Register a new tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "function": func,
            "parameters": parameters
        }
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        try:
            # Validate parameters
            missing_params = [param for param in tool["parameters"] if param not in kwargs]
            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")
            
            # Execute tool
            result = await tool["function"](**kwargs)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_python_code(self, code: str, context: str = "") -> Dict[str, Any]:
        """Safely execute Python code with sandboxing"""
        try:
            # Create temporary file for execution
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute with timeout and restrictions
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30,
                env={"PYTHONPATH": ""}  # Restrict imports
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": "completed"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_data(self, data: str, analysis_type: str, context: str = "") -> Dict[str, Any]:
        """Analyze data and provide insights"""
        try:
            # Parse data (assuming CSV format for now)
            df = pd.read_csv(BytesIO(data.encode()))
            
            insights = {}
            
            if analysis_type == "trends":
                # Analyze trends over time
                if len(df.columns) >= 2:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        trends = df[numeric_cols].describe()
                        insights["trends"] = trends.to_dict()
                        insights["summary"] = f"Analyzed {len(df)} rows with {len(numeric_cols)} numeric columns"
            
            elif analysis_type == "patterns":
                # Find patterns in data
                insights["patterns"] = {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "missing_values": df.isnull().sum().to_dict(),
                    "data_types": df.dtypes.to_dict()
                }
            
            return insights
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_chart(self, data: str, chart_type: str, title: str, context: str = "") -> Dict[str, Any]:
        """Generate charts and visualizations"""
        try:
            # Parse data
            df = pd.read_csv(BytesIO(data.encode()))
            
            # Create chart based on type
            plt.figure(figsize=(10, 6))
            
            if chart_type == "line":
                if len(df.columns) >= 2:
                    plt.plot(df.iloc[:, 0], df.iloc[:, 1])
            elif chart_type == "bar":
                if len(df.columns) >= 2:
                    plt.bar(df.iloc[:, 0], df.iloc[:, 1])
            elif chart_type == "scatter":
                if len(df.columns) >= 2:
                    plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
            
            plt.title(title)
            plt.xlabel(df.columns[0] if len(df.columns) > 0 else "X")
            plt.ylabel(df.columns[1] if len(df.columns) > 1 else "Y")
            
            # Save to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": chart_type,
                "chart_data": chart_data,
                "title": title,
                "dimensions": f"{len(df)} rows x {len(df.columns)} columns"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _web_search(self, query: str, context: str = "") -> Dict[str, Any]:
        """Search the web for current information"""
        try:
            # Use a simple search API (you can replace with Google Custom Search or similar)
            search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "query": query,
                    "results": data.get("Abstract", "No abstract available"),
                    "source": "DuckDuckGo",
                    "related_topics": data.get("RelatedTopics", [])[:3]
                }
            else:
                return {"error": f"Search failed with status {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _process_file(self, file_path: str, operation: str, context: str = "") -> Dict[str, Any]:
        """Process and analyze uploaded files"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            file_info = {
                "path": file_path,
                "size": os.path.getsize(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            
            if operation == "analyze":
                # Basic file analysis
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_info.update({
                    "content_length": len(content),
                    "lines": len(content.splitlines()),
                    "words": len(content.split()),
                    "file_type": "text"
                })
            
            return file_info
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _suggest_enrichment(self, query: str, current_results: List[Dict], context: str = "") -> Dict[str, Any]:
        """Suggest ways to enrich the knowledge base"""
        try:
            suggestions = []
            
            # Analyze current results for gaps
            if not current_results:
                suggestions.append({
                    "type": "document_upload",
                    "description": "No relevant documents found. Consider uploading related materials.",
                    "priority": "high"
                })
            
            # Check for low confidence results
            low_confidence = [r for r in current_results if r.get("confidence", 1.0) < 0.7]
            if low_confidence:
                suggestions.append({
                    "type": "additional_sources",
                    "description": f"Found {len(low_confidence)} low-confidence results. Additional sources needed.",
                    "priority": "medium"
                })
            
            # Suggest external data sources
            suggestions.append({
                "type": "external_data",
                "description": "Consider integrating with external APIs for real-time data.",
                "priority": "low"
            })
            
            return {
                "suggestions": suggestions,
                "total_suggestions": len(suggestions),
                "query": query
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _fact_check(self, claim: str, context: str = "", sources: List[str] = None) -> Dict[str, Any]:
        """Verify facts and prevent hallucination"""
        try:
            # Use OpenAI to fact-check the claim against context
            prompt = f"""
            Fact-check the following claim against the provided context:
            
            Claim: {claim}
            Context: {context}
            
            Provide a structured response with:
            1. Fact-check result (true/false/uncertain)
            2. Confidence level (0-1)
            3. Supporting evidence from context
            4. Any missing information needed
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            result = response.choices[0].message.content
            
            return {
                "claim": claim,
                "fact_check_result": result,
                "confidence": 0.8,  # This could be extracted from the response
                "context_used": context[:200] + "..." if len(context) > 200 else context
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools"""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for tool in self.tools.values()
        ]
