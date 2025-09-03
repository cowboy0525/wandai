// Types for Wand AI Frontend Components

// Task-related types
export interface TaskRequest {
  description: string;
  priority: 'low' | 'medium' | 'high';
  context?: string;
  deadline?: string;
}

export interface TaskResult {
  task_id: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  result: string;
  metadata?: Record<string, any>;
  created_at: string;
  completed_at?: string;
  agent_results?: AgentResult[];
}

export interface AgentResult {
  agent_name: string;
  status: AgentStatus;
  output: string;
  confidence: number;
  tools_used: string[];
  execution_time: number;
  metadata?: Record<string, any>;
}

// Agent status enum
export enum AgentStatus {
  PLANNING = 'PLANNING',
  EXECUTING = 'EXECUTING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  WAITING = 'WAITING'
}

// Search-related types
export interface SearchQuery {
  query: string;
  top_k: number;
  filters?: SearchFilters;
  strategy?: 'semantic' | 'keyword' | 'hybrid';
}

export interface SearchFilters {
  document_type?: string[];
  date_range?: {
    start: string;
    end: string;
  };
  confidence_threshold?: number;
  tags?: string[];
}

export interface SearchResult {
  id: string;
  content: string;
  metadata: {
    document_type: string;
    source: string;
    created_at: string;
    tags: string[];
    confidence: number;
    relevance_score: number;
  };
  highlights?: string[];
  chunks?: DocumentChunk[];
}

export interface DocumentChunk {
  id: string;
  content: string;
  metadata: {
    chunk_index: number;
    confidence: number;
    relevance_score: number;
  };
}

// Knowledge enrichment types
export interface EnrichmentSuggestion {
  id: string;
  type: 'document' | 'tag' | 'relationship' | 'metadata';
  description: string;
  priority: 'low' | 'medium' | 'high';
  confidence: number;
  action_required: boolean;
  estimated_effort: string;
}

// Document upload types
export interface DocumentUpload {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  metadata?: {
    document_type: string;
    size: number;
    pages?: number;
    tags?: string[];
  };
  error?: string;
}

export interface UploadResult {
  success: boolean;
  document_id: string;
  message: string;
  metadata?: Record<string, any>;
}

// Dashboard and analytics types
export interface DashboardMetrics {
  total_documents: number;
  total_tasks: number;
  active_agents: number;
  system_health: 'excellent' | 'good' | 'fair' | 'poor';
  recent_activity: ActivityItem[];
  performance_metrics: PerformanceMetrics;
}

export interface ActivityItem {
  id: string;
  type: 'task_completed' | 'document_uploaded' | 'search_performed' | 'agent_activated';
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface PerformanceMetrics {
  average_task_completion_time: number;
  search_accuracy: number;
  agent_success_rate: number;
  system_uptime: number;
  error_rate: number;
}

// Agent management types
export interface AgentInfo {
  name: string;
  role: string;
  capabilities: string[];
  status: AgentStatus;
  performance: {
    success_rate: number;
    execution_count: number;
    average_execution_time: number;
    last_execution: string;
  };
  available_tools: string[];
}

export interface ToolInfo {
  name: string;
  description: string;
  parameters: ToolParameter[];
  usage_count: number;
  success_rate: number;
}

export interface ToolParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description: string;
  required: boolean;
  default_value?: any;
}

// Context and workflow types
export interface WorkflowContext {
  workflow_id: string;
  current_phase: string;
  phase_progress: number;
  agent_assignments: Record<string, string>;
  dependencies: string[];
  quality_checkpoints: string[];
  estimated_completion: string;
}

export interface ContextItem {
  id: string;
  agent_name: string;
  content: string;
  timestamp: string;
  relevance_score: number;
  context_type: 'input' | 'output' | 'intermediate' | 'final';
}

// Error and notification types
export interface AppError {
  id: string;
  type: 'validation' | 'execution' | 'system' | 'network';
  message: string;
  details?: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action_required: boolean;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  metadata?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Chart and visualization types
export interface ChartData {
  type: 'line' | 'bar' | 'pie' | 'scatter';
  title: string;
  data: {
    x: string[] | number[];
    y: number[];
  };
  options?: Record<string, any>;
}

export interface VisualizationResult {
  chart_type: string;
  title: string;
  data: any;
  image_base64?: string;
  message: string;
  success: boolean;
}

// Task execution workflow types
export interface ExecutionPhase {
  name: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  progress: number;
  start_time?: string;
  end_time?: string;
  agent_assigned?: string;
  output?: string;
  dependencies: string[];
}

export interface WorkflowExecution {
  workflow_id: string;
  task_description: string;
  phases: ExecutionPhase[];
  overall_progress: number;
  status: 'planning' | 'executing' | 'reviewing' | 'completed' | 'failed';
  start_time: string;
  estimated_completion?: string;
  quality_score?: number;
}

// Knowledge base analysis types
export interface KnowledgeAnalysis {
  coverage_score: number;
  knowledge_gaps: string[];
  enrichment_opportunities: EnrichmentSuggestion[];
  quality_metrics: {
    completeness: number;
    accuracy: number;
    relevance: number;
    consistency: number;
  };
  recommendations: string[];
}

// Agent coordination types
export interface CoordinationResult {
  phases_completed: string[];
  agent_performance: Record<string, AgentPerformance>;
  dependencies_met: string[];
  quality_checkpoints_passed: string[];
  risks_mitigated: string[];
  overall_progress: number;
  summary: string;
}

export interface AgentPerformance {
  agent_name: string;
  tasks_completed: number;
  success_rate: number;
  average_execution_time: number;
  tools_used: string[];
  confidence_level: number;
}

// Quality assurance types
export interface QualityCheck {
  overall_quality: 'excellent' | 'good' | 'fair' | 'poor';
  quality_score: number;
  issues_found: string[];
  recommendations: string[];
  confidence: number;
  check_timestamp: string;
}

// Export all types
export type {
  TaskRequest,
  TaskResult,
  AgentResult,
  SearchQuery,
  SearchFilters,
  SearchResult,
  DocumentChunk,
  EnrichmentSuggestion,
  DocumentUpload,
  UploadResult,
  DashboardMetrics,
  ActivityItem,
  PerformanceMetrics,
  AgentInfo,
  ToolInfo,
  ToolParameter,
  WorkflowContext,
  ContextItem,
  AppError,
  Notification,
  ApiResponse,
  PaginatedResponse,
  ChartData,
  VisualizationResult,
  ExecutionPhase,
  WorkflowExecution,
  KnowledgeAnalysis,
  CoordinationResult,
  AgentPerformance,
  QualityCheck
};

