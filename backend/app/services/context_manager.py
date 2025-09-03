import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages context sharing between agents with intelligent filtering and summarization"""
    
    def __init__(self):
        self.shared_context = {}
        self.agent_outputs = {}
        self.context_history = []
        self.context_metadata = {}
    
    def add_agent_output(self, agent_name: str, output: str, metadata: Dict[str, Any] = None):
        """Store agent output with metadata"""
        timestamp = datetime.now()
        
        self.agent_outputs[agent_name] = {
            "output": output,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "context_id": f"{agent_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Add to context history
        self.context_history.append({
            "agent": agent_name,
            "timestamp": timestamp,
            "output_length": len(output),
            "has_metadata": bool(metadata)
        })
        
        # Keep only last 50 outputs
        if len(self.context_history) > 50:
            self.context_history.pop(0)
    
    def create_context(self, task_id: str, context: List[Any]) -> Dict[str, Any]:
        """Create a new context for a task"""
        try:
            # Convert context to string representation
            context_text = ""
            if context:
                if hasattr(context[0], 'content'):
                    context_text = "\n\n".join([f"Context {i+1}: {item.content[:300]}..." for i, item in enumerate(context[:3])])
                else:
                    context_text = str(context)
            
            task_context = {
                "task_id": task_id,
                "created_at": datetime.now(),
                "context_data": context_text,
                "agent_results": {},
                "shared_data": {}
            }
            
            self.shared_context[task_id] = task_context
            return task_context
            
        except Exception as e:
            logger.error(f"Context creation failed: {str(e)}")
            return {
                "task_id": task_id,
                "created_at": datetime.now(),
                "context_data": "",
                "agent_results": {},
                "shared_data": {}
            }
    
    def update_context(self, task_id: str, agent_name: str, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Update context with agent results"""
        try:
            if task_id not in self.shared_context:
                self.shared_context[task_id] = {
                    "task_id": task_id,
                    "created_at": datetime.now(),
                    "context_data": "",
                    "agent_results": {},
                    "shared_data": {}
                }
            
            # Store agent result
            self.shared_context[task_id]["agent_results"][agent_name] = {
                "output": agent_result.get("output", ""),
                "confidence": agent_result.get("confidence", 0.0),
                "tools_used": agent_result.get("tools_used", []),
                "timestamp": datetime.now()
            }
            
            # Update shared data if available
            if "metadata" in agent_result:
                self.shared_context[task_id]["shared_data"].update(agent_result["metadata"])
            
            return self.shared_context[task_id]
            
        except Exception as e:
            logger.error(f"Context update failed: {str(e)}")
            return self.shared_context.get(task_id, {})
    
    def get_context_for_agent(self, agent_name: str, task: str, max_context_size: int = 2000) -> str:
        """Get relevant context for a specific agent and task"""
        try:
            # Analyze task to determine relevant context
            relevant_contexts = self._identify_relevant_contexts(agent_name, task)
            
            # Filter and prioritize context
            filtered_context = self._filter_context_by_relevance(relevant_contexts, task)
            
            # Summarize if context is too long
            if len(filtered_context) > max_context_size:
                filtered_context = self._summarize_context(filtered_context, max_context_size)
            
            return filtered_context
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return "Context retrieval failed. Proceeding with limited context."
    
    def _identify_relevant_contexts(self, agent_name: str, task: str) -> List[Dict[str, Any]]:
        """Identify which contexts are most relevant to the agent and task"""
        relevant_contexts = []
        task_lower = task.lower()
        
        for agent, output_data in self.agent_outputs.items():
            relevance_score = self._calculate_context_relevance(
                agent, output_data, agent_name, task_lower
            )
            
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_contexts.append({
                    "agent": agent,
                    "output": output_data["output"],
                    "metadata": output_data["metadata"],
                    "relevance_score": relevance_score,
                    "timestamp": output_data["timestamp"]
                })
        
        # Sort by relevance score (highest first)
        relevant_contexts.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_contexts
    
    def _calculate_context_relevance(self, context_agent: str, output_data: Dict[str, Any], 
                                   target_agent: str, task: str) -> float:
        """Calculate how relevant a context is to the current agent and task"""
        relevance_score = 0.0
        
        # Agent relationship relevance
        if context_agent == target_agent:
            relevance_score += 0.3  # Same agent's previous outputs
        elif self._are_agents_related(context_agent, target_agent):
            relevance_score += 0.2  # Related agents
        
        # Task relevance
        task_relevance = self._calculate_task_relevance(output_data["output"], task)
        relevance_score += task_relevance * 0.5
        
        # Recency relevance (newer = more relevant)
        time_diff = datetime.now() - output_data["timestamp"]
        recency_score = max(0, 1 - (time_diff.total_seconds() / 3600))  # Decay over 1 hour
        relevance_score += recency_score * 0.2
        
        return min(relevance_score, 1.0)
    
    def _are_agents_related(self, agent1: str, agent2: str) -> bool:
        """Check if two agents are related in the workflow"""
        # Define agent relationships
        agent_groups = {
            "planning": ["planner", "coordinator"],
            "execution": ["research", "analysis", "creator"],
            "review": ["coordinator", "planner"]
        }
        
        for group in agent_groups.values():
            if agent1.lower() in group and agent2.lower() in group:
                return True
        
        return False
    
    def _calculate_task_relevance(self, context_text: str, task: str) -> float:
        """Calculate how relevant context text is to the current task"""
        try:
            # Simple keyword matching (in production, use more sophisticated NLP)
            task_words = set(task.lower().split())
            context_words = set(context_text.lower().split())
            
            if not task_words:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(task_words.intersection(context_words))
            union = len(task_words.union(context_words))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception:
            return 0.0
    
    def _filter_context_by_relevance(self, relevant_contexts: List[Dict[str, Any]], task: str) -> str:
        """Filter and combine relevant contexts"""
        if not relevant_contexts:
            return "No relevant context available."
        
        # Combine top relevant contexts
        combined_context = []
        
        for context in relevant_contexts[:5]:  # Top 5 most relevant
            agent_name = context["agent"]
            output = context["output"]
            relevance = context["relevance_score"]
            
            # Format context entry
            context_entry = f"[{agent_name} - Relevance: {relevance:.2f}]\n{output}\n"
            combined_context.append(context_entry)
        
        return "\n---\n".join(combined_context)
    
    def _summarize_context(self, context: str, max_size: int) -> str:
        """Summarize context if it's too long"""
        try:
            if len(context) <= max_size:
                return context
            
            # Simple summarization by taking first part and indicating truncation
            summary = context[:max_size - 100] + "...\n\n[Context truncated for length. Full context available in agent outputs.]"
            return summary
            
        except Exception as e:
            logger.error(f"Context summarization failed: {str(e)}")
            return context[:max_size] + "..."
    
    def get_agent_context_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get a summary of context for a specific agent"""
        try:
            agent_contexts = [
                ctx for ctx in self.context_history 
                if ctx["agent"] == agent_name
            ]
            
            if not agent_contexts:
                return {
                    "agent": agent_name,
                    "context_count": 0,
                    "last_activity": None,
                    "total_output_length": 0
                }
            
            total_length = sum(ctx["output_length"] for ctx in agent_contexts)
            last_activity = max(ctx["timestamp"] for ctx in agent_contexts)
            
            return {
                "agent": agent_name,
                "context_count": len(agent_contexts),
                "last_activity": last_activity.isoformat(),
                "total_output_length": total_length,
                "average_output_length": total_length / len(agent_contexts)
            }
            
        except Exception as e:
            logger.error(f"Agent context summary failed: {str(e)}")
            return {"agent": agent_name, "error": str(e)}
    
    def get_workflow_context(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get context for a specific workflow or overall system"""
        try:
            # Get recent activity
            recent_agents = [ctx["agent"] for ctx in self.context_history[-10:]]
            
            # Get context statistics
            total_contexts = len(self.context_history)
            unique_agents = len(set(ctx["agent"] for ctx in self.context_history))
            
            # Get context distribution
            agent_distribution = {}
            for ctx in self.context_history:
                agent = ctx["agent"]
                agent_distribution[agent] = agent_distribution.get(agent, 0) + 1
            
            return {
                "workflow_id": workflow_id or "system",
                "total_contexts": total_contexts,
                "unique_agents": unique_agents,
                "recent_agents": recent_agents,
                "agent_distribution": agent_distribution,
                "context_timeline": [
                    {
                        "timestamp": ctx["timestamp"].isoformat(),
                        "agent": ctx["agent"],
                        "action": "context_added"
                    }
                    for ctx in self.context_history[-20:]  # Last 20 contexts
                ]
            }
            
        except Exception as e:
            logger.error(f"Workflow context retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    def clear_old_context(self, max_age_hours: int = 24):
        """Clear context older than specified age"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            # Clear old agent outputs
            agents_to_remove = []
            for agent, output_data in self.agent_outputs.items():
                if output_data["timestamp"].timestamp() < cutoff_time:
                    agents_to_remove.append(agent)
            
            for agent in agents_to_remove:
                del self.agent_outputs[agent]
            
            # Clear old context history
            self.context_history = [
                ctx for ctx in self.context_history
                if ctx["timestamp"].timestamp() >= cutoff_time
            ]
            
            logger.info(f"Cleared {len(agents_to_remove)} old agent outputs and {len(self.context_history)} old context entries")
            
        except Exception as e:
            logger.error(f"Context cleanup failed: {str(e)}")
    
    def export_context(self, format_type: str = "json") -> str:
        """Export context data in specified format"""
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_outputs": self.agent_outputs,
                "context_history": self.context_history,
                "shared_context": self.shared_context
            }
            
            if format_type.lower() == "json":
                return json.dumps(export_data, indent=2, default=str)
            else:
                return str(export_data)
                
        except Exception as e:
            logger.error(f"Context export failed: {str(e)}")
            return f"Export failed: {str(e)}"
    
    def import_context(self, context_data: str, format_type: str = "json"):
        """Import context data from external source"""
        try:
            if format_type.lower() == "json":
                data = json.loads(context_data)
            else:
                data = eval(context_data)  # Be careful with eval in production
            
            # Validate data structure
            if isinstance(data, dict) and "agent_outputs" in data:
                self.agent_outputs.update(data["agent_outputs"])
                self.context_history.extend(data.get("context_history", []))
                self.shared_context.update(data.get("shared_context", {}))
                
                logger.info("Context imported successfully")
            else:
                raise ValueError("Invalid context data format")
                
        except Exception as e:
            logger.error(f"Context import failed: {str(e)}")
            raise
