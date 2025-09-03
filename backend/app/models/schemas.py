from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enums
class AgentStatus(str, Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class DocumentType(str, Enum):
    REPORT = "report"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"
    OTHER = "other"

class EnrichmentType(str, Enum):
    DOCUMENT_UPLOAD = "document_upload"
    ADDITIONAL_SOURCES = "additional_sources"
    DOCUMENT_DIVERSITY = "document_diversity"
    EXTERNAL_INTEGRATION = "external_integration"
    USER_FEEDBACK = "user_feedback"

class CompletenessLevel(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    INCOMPLETE = "incomplete"
    ERROR = "error"

# Base Models
class BaseSchema(BaseModel):
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Agent Models
class AgentInfo(BaseModel):
    agent_id: str
    name: str
    role: str
    status: AgentStatus
    progress: float = Field(ge=0.0, le=100.0)
    capabilities: List[str] = []
    tools_available: List[str] = []

class AgentResult(BaseModel):
    agent_name: str
    output: str
    confidence: float = Field(ge=0.0, le=1.0)
    tools_used: List[str] = []
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}
    validation_status: Dict[str, Any] = {}

# Task Models
class TaskRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Detailed task description")
    priority: TaskPriority = TaskPriority.MEDIUM
    context: Optional[str] = None
    expected_duration: Optional[int] = None  # in minutes
    required_agents: Optional[List[str]] = []
    constraints: Optional[Dict[str, Any]] = {}

class TaskStatus(BaseModel):
    task_id: str
    description: str
    status: AgentStatus
    created_at: datetime
    updated_at: datetime
    agents: List[AgentInfo] = []
    progress: float = Field(ge=0.0, le=1.0)
    result: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    estimated_completion: Optional[datetime] = None

class TaskResult(BaseModel):
    task_id: str
    status: AgentStatus
    final_result: Dict[str, Any]
    agent_summaries: List[Dict[str, Any]]
    knowledge_gaps: List[Dict[str, Any]]
    execution_time: float
    created_at: datetime
    completed_at: datetime
    overall_confidence: float = Field(ge=0.0, le=1.0)
    quality_score: Optional[float] = None

# Knowledge Base Models
class DocumentMetadata(BaseModel):
    filename: str
    document_type: DocumentType = DocumentType.OTHER
    upload_date: datetime = Field(default_factory=datetime.now)
    file_size: int = 0
    source_reliability: str = "medium"
    tags: List[str] = []
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None

class SearchResult(BaseModel):
    document_id: str
    content: str
    metadata: DocumentMetadata
    relevance_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    search_timestamp: datetime = Field(default_factory=datetime.now)
    chunk_index: Optional[int] = None
    knowledge_areas: List[str] = []

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3)
    filters: Optional[Dict[str, Any]] = {}
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    completeness_score: float = Field(ge=0.0, le=1.0)
    suggestions: List[str] = []

# Completeness and Enrichment Models
class CompletenessCheck(BaseModel):
    completeness_level: CompletenessLevel
    confidence: float = Field(ge=0.0, le=1.0)
    missing_information: str
    quality_score: float = Field(ge=0.0, le=1.0)
    recommendations: str
    gaps_identified: List[str] = []

class EnrichmentSuggestion(BaseModel):
    type: EnrichmentType
    description: str
    priority: str = "medium"  # low, medium, high
    expected_impact: str = "medium"  # low, medium, high
    related_queries: List[str] = []
    implementation_steps: Optional[List[str]] = []
    estimated_effort: Optional[str] = None

# Tool Models
class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: List[str]
    category: str = "general"
    availability: bool = True

class ToolExecution(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    execution_time: float
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# AI Answer Models
class AIAnswer(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    completeness: CompletenessLevel
    missing_info: str
    sources_used: List[str] = []
    suggestions: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)

# Context and Workflow Models
class ContextItem(BaseModel):
    type: str  # "document", "agent_output", "user_input", "tool_result"
    content: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class WorkflowStep(BaseModel):
    step_id: str
    agent_name: str
    action: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    status: str
    duration: float
    tools_used: List[str] = []

class WorkflowExecution(BaseModel):
    workflow_id: str
    task_id: str
    steps: List[WorkflowStep]
    current_step: int = 0
    status: str
    start_time: datetime
    estimated_completion: Optional[datetime] = None

# Performance and Analytics Models
class PerformanceMetrics(BaseModel):
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    average_execution_time: float = 0.0
    success_rate: float = Field(ge=0.0, le=1.0)
    last_execution: Optional[datetime] = None
    tools_usage: Dict[str, int] = {}

class SystemHealth(BaseModel):
    overall_status: str  # "healthy", "warning", "critical"
    agent_health: Dict[str, str]
    tool_availability: Dict[str, bool]
    knowledge_base_status: str
    last_check: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = []

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Real-time Communication Models
class ProgressUpdate(BaseModel):
    type: str  # "status_update", "progress", "completion", "error"
    task_id: str
    status: Optional[str] = None
    progress: Optional[float] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# Validation Models
class ValidationResult(BaseModel):
    valid: bool
    reason: str
    confidence: str  # "low", "medium", "high"
    suggestions: List[str] = []
    issues_found: List[str] = []

# Configuration Models
class SystemConfiguration(BaseModel):
    max_concurrent_tasks: int = 5
    agent_timeout: int = 300  # seconds
    max_retries: int = 3
    enable_fact_checking: bool = True
    enable_tool_validation: bool = True
    log_level: str = "INFO"
    debug_mode: bool = False
