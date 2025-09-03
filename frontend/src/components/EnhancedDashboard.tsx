import React, { useState, useEffect } from 'react';
import { TaskResult, SearchResult, EnrichmentSuggestion } from '../types';

interface EnhancedDashboardProps {
  recentTasks: TaskResult[];
  recentSearches: SearchResult[];
  recentSuggestions: EnrichmentSuggestion[];
}

interface SystemMetrics {
  totalDocuments: number;
  totalChunks: number;
  coverageAreas: string[];
  lastUpdated: string;
  averageChunksPerDocument: number;
}

interface AgentMetrics {
  totalTasks: number;
  successfulTasks: number;
  failedTasks: number;
  successRate: number;
  averageExecutionTime: number;
  activeAgents: number;
  availableTools: number;
}

const EnhancedDashboard: React.FC<EnhancedDashboardProps> = ({
  recentTasks,
  recentSearches,
  recentSuggestions
}) => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [agentMetrics, setAgentMetrics] = useState<AgentMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch system metrics
      const systemResponse = await fetch('/api/v1/documents/');
      if (systemResponse.ok) {
        const systemData = await systemResponse.json();
        setSystemMetrics({
          totalDocuments: systemData.total_documents || 0,
          totalChunks: systemData.total_chunks || 0,
          coverageAreas: systemData.coverage_areas || [],
          lastUpdated: systemData.last_updated || 'Unknown',
          averageChunksPerDocument: systemData.average_chunks_per_document || 0
        });
      }

      // Fetch agent metrics
      const agentResponse = await fetch('/api/v1/tasks/');
      if (agentResponse.ok) {
        const agentData = await agentResponse.json();
        const totalTasks = agentData.total_tasks || 0;
        const successfulTasks = agentData.successful_tasks || 0;
        const failedTasks = agentData.failed_tasks || 0;
        
        setAgentMetrics({
          totalTasks,
          successfulTasks,
          failedTasks,
          successRate: totalTasks > 0 ? (successfulTasks / totalTasks) * 100 : 0,
          averageExecutionTime: agentData.average_execution_time || 0,
          activeAgents: agentData.active_agents || 5,
          availableTools: agentData.available_tools || 4
        });
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'executing': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading dashboard: {error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <h1 className="text-4xl font-bold text-gray-800">Enhanced Dashboard</h1>
      
      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* System Health */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className="text-2xl font-bold text-gray-900">
                {systemMetrics?.totalDocuments ? 'Healthy' : 'No Data'}
              </p>
            </div>
          </div>
        </div>

        {/* Total Documents */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">{systemMetrics?.totalDocuments || 0}</p>
            </div>
          </div>
        </div>

        {/* Success Rate */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-full">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {(agentMetrics?.successRate || 0).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        {/* Active Agents */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Agents</p>
              <p className="text-2xl font-bold text-gray-900">{agentMetrics?.activeAgents || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Statistics */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">System Statistics</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Chunks</span>
              <span className="font-medium">{systemMetrics?.totalChunks || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Chunks per Document</span>
              <span className="font-medium">{(systemMetrics?.averageChunksPerDocument || 0).toFixed(1)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Updated</span>
              <span className="font-medium">{systemMetrics?.lastUpdated || 'Unknown'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Coverage Areas</span>
              <span className="font-medium">{systemMetrics?.coverageAreas.length || 0}</span>
            </div>
          </div>
          
          {/* Coverage Areas */}
          {systemMetrics?.coverageAreas && systemMetrics.coverageAreas.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Knowledge Coverage</h3>
              <div className="flex flex-wrap gap-2">
                {systemMetrics.coverageAreas.map((area, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {area}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Agent Performance */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Agent Performance</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Tasks</span>
              <span className="font-medium">{agentMetrics?.totalTasks || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Successful Tasks</span>
              <span className="font-medium text-green-600">{agentMetrics?.successfulTasks || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Failed Tasks</span>
              <span className="font-medium text-red-600">{agentMetrics?.failedTasks || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Execution Time</span>
              <span className="font-medium">{formatDuration(agentMetrics?.averageExecutionTime || 0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Available Tools</span>
              <span className="font-medium">{agentMetrics?.availableTools || 0}</span>
            </div>
          </div>

          {/* Success Rate Chart */}
          <div className="mt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Success Rate</span>
              <span className="text-sm text-gray-500">{(agentMetrics?.successRate || 0).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${agentMetrics?.successRate || 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Tasks */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Tasks</h2>
          <div className="space-y-3">
            {recentTasks.length > 0 ? (
              recentTasks.slice(0, 5).map((task, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatDuration(task.execution_time)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 line-clamp-2">{task.description}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No recent tasks</p>
            )}
          </div>
        </div>

        {/* Recent Searches */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Searches</h2>
          <div className="space-y-3">
            {recentSearches.length > 0 ? (
              recentSearches.slice(0, 5).map((search, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">
                      {(search.relevance_score * 100).toFixed(0)}% relevant
                    </span>
                    <span className="text-xs text-gray-500">
                      {search.filename}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 line-clamp-2">{search.content_snippet}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No recent searches</p>
            )}
          </div>
        </div>

        {/* Recent Suggestions */}
        <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Enrichment Suggestions</h2>
          <div className="space-y-3">
            {recentSuggestions.length > 0 ? (
              recentSuggestions.slice(0, 5).map((suggestion, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(suggestion.priority)}`}>
                      {suggestion.priority}
                    </span>
                    <span className="text-xs text-gray-500">
                      {suggestion.suggestion_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 line-clamp-2">{suggestion.description}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No recent suggestions</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button className="p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors">
            <div className="text-center">
              <div className="text-2xl mb-2">📄</div>
              <span className="text-sm font-medium text-blue-800">Upload Document</span>
            </div>
          </button>
          
          <button className="p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors">
            <div className="text-center">
              <div className="text-2xl mb-2">🔍</div>
              <span className="text-sm font-medium text-green-800">Search Knowledge</span>
            </div>
          </button>
          
          <button className="p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors">
            <div className="text-center">
              <div className="text-2xl mb-2">🤖</div>
              <span className="text-sm font-medium text-purple-800">Execute Task</span>
            </div>
          </button>
          
          <button className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 transition-colors">
            <div className="text-center">
              <div className="text-2xl mb-2">📊</div>
              <span className="text-sm font-medium text-yellow-800">View Analytics</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;
