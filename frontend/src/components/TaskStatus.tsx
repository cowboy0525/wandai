import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface TaskStatusProps {
  taskId: string | null;
}

interface AgentInfo {
  id: string;
  name: string;
  role: string;
  status: string;
  current_task?: string;
  progress: number;
}

interface TaskStatusData {
  task_id: string;
  description: string;
  status: string;
  agents: AgentInfo[];
  progress: number;
  estimated_completion?: string;
  results?: any;
  errors?: string[];
}

const TaskStatus: React.FC<TaskStatusProps> = ({ taskId }) => {
  const [taskStatus, setTaskStatus] = useState<TaskStatusData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (taskId && taskId !== 'unknown') {
      fetchTaskStatus();
      // Poll for updates every 2 seconds
      const interval = setInterval(fetchTaskStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [taskId]);

  const fetchTaskStatus = async () => {
    if (!taskId || taskId === 'unknown') return;
    
    try {
      setLoading(true);
      const response = await axios.get(`/task-status/${taskId}`);
      setTaskStatus(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch task status');
    } finally {
      setLoading(false);
    }
  };

  const toggleResultExpansion = (resultId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId);
    } else {
      newExpanded.add(resultId);
    }
    setExpandedResults(newExpanded);
  };

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'planning':
        return 'text-yellow-600 bg-yellow-100';
      case 'executing':
        return 'text-blue-600 bg-blue-100';
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'planning':
        return '🤔';
      case 'executing':
        return '⚡';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      default:
        return '❓';
    }
  };

  const formatProgress = (progress: number): string => {
    return `${Math.round(progress * 100)}%`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!taskId || taskId === 'unknown') {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <div className="text-4xl mb-4">📊</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Task</h3>
        <p className="text-gray-500">
          Submit a task in the Task Execution tab to see its status and progress here.
        </p>
      </div>
    );
  }

  if (loading && !taskStatus) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-500">Loading task status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-6">
        <div className="flex">
          <div className="text-red-400 text-2xl">⚠️</div>
          <div className="ml-3">
            <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading Task</h3>
            <p className="text-red-700">{error}</p>
            <button
              onClick={fetchTaskStatus}
              className="mt-3 px-4 py-2 bg-red-100 text-red-800 rounded-md hover:bg-red-200 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!taskStatus) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <div className="text-4xl mb-4">❓</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Task Not Found</h3>
        <p className="text-gray-500">
          The requested task could not be found. It may have been completed or removed.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Task Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Task: {taskStatus.description}
            </h3>
            <p className="text-sm text-gray-500">ID: {taskStatus.task_id}</p>
          </div>
          <div className="text-right">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(taskStatus.status)}`}>
              <span className="mr-2">{getStatusIcon(taskStatus.status)}</span>
              {taskStatus.status.charAt(0).toUpperCase() + taskStatus.status.slice(1)}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{formatProgress(taskStatus.progress)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${taskStatus.progress * 100}%` }}
            />
          </div>
        </div>

        {taskStatus.estimated_completion && (
          <p className="text-sm text-gray-500">
            Estimated completion: {formatDate(taskStatus.estimated_completion)}
          </p>
        )}
      </div>

      {/* Agent Status */}
      {taskStatus.agents && taskStatus.agents.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              AI Agent Status ({taskStatus.agents.length})
            </h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {taskStatus.agents.map((agent) => (
              <div key={agent.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-2xl">🤖</div>
                    <div>
                      <p className="font-medium text-gray-900">{agent.name}</p>
                      <p className="text-sm text-gray-500">{agent.role}</p>
                      {agent.current_task && (
                        <p className="text-sm text-blue-600 mt-1">
                          Current: {agent.current_task}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="mb-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                        {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Progress: {formatProgress(agent.progress)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Task Results */}
      {taskStatus.results && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Task Results
            </h3>
          </div>
          
          <div className="p-6">
            {taskStatus.results.final_report && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Final Report</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <ReactMarkdown className="prose prose-sm max-w-none">
                    {taskStatus.results.final_report}
                  </ReactMarkdown>
                </div>
              </div>
            )}
            
            {taskStatus.results.agent_contributions && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Agent Contributions</h4>
                <p className="text-sm text-gray-600">
                  {taskStatus.results.agent_contributions} AI agents contributed to this task.
                </p>
              </div>
            )}
            
            {taskStatus.results.completion_timestamp && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Completion Details</h4>
                <p className="text-sm text-gray-600">
                  Completed at: {formatDate(taskStatus.results.completion_timestamp)}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Errors */}
      {taskStatus.errors && taskStatus.errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-6">
          <h3 className="text-lg font-medium text-red-800 mb-3">Errors Encountered</h3>
          <div className="space-y-2">
            {taskStatus.errors.map((error, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="text-red-400">⚠️</div>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchTaskStatus}
          disabled={loading}
          className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : '🔄 Refresh Status'}
        </button>
      </div>
    </div>
  );
};

export default TaskStatus;
