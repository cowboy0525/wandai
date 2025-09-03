from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    MD = "md"

@dataclass
class Document:
    """Domain model for a document"""
    doc_id: str
    filename: str
    file_type: DocumentType
    content: str
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_summary(self, summary: str):
        """Update document summary"""
        self.summary = summary
        self.updated_at = datetime.utcnow()
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to document"""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

@dataclass
class Agent:
    """Domain model for an AI agent"""
    agent_id: str
    name: str
    role: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "idle"
    progress: float = 0.0
    
    def update_status(self, status: str, progress: float = None):
        """Update agent status and progress"""
        self.status = status
        if progress is not None:
            self.progress = progress
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        return task_type in self.capabilities

@dataclass
class Task:
    """Domain model for a task"""
    task_id: str
    description: str
    priority: str = "medium"
    deadline: Optional[datetime] = None
    status: str = "pending"
    agents: List[Agent] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def start_execution(self):
        """Mark task as started"""
        self.status = "executing"
        self.started_at = datetime.utcnow()
    
    def complete(self, results: Dict[str, Any]):
        """Mark task as completed with results"""
        self.status = "completed"
        self.results = results
        self.completed_at = datetime.utcnow()
    
    def add_agent(self, agent: Agent):
        """Add an agent to the task"""
        self.agents.append(agent)

@dataclass
class KnowledgeGap:
    """Domain model for identified knowledge gaps"""
    gap_id: str
    description: str
    suggestion_type: str
    priority: str = "medium"
    related_queries: List[str] = field(default_factory=list)
    identified_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    
    def mark_resolved(self):
        """Mark knowledge gap as resolved"""
        self.resolved = True
    
    def add_related_query(self, query: str):
        """Add a related search query"""
        if query not in self.related_queries:
            self.related_queries.append(query)
