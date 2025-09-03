import React, { useState, useEffect } from 'react';
import { TaskRequest, TaskResult, AgentStatus } from '../types';

interface EnhancedTaskExecutionProps {
  onTaskComplete: (result: TaskResult) => void;
}

interface AgentProgress {
  name: string;
  status: AgentStatus;
  progress: number;
  output: string;
  confidence: number;
}

const EnhancedTaskExecution: React.FC<EnhancedTaskExecutionProps> = ({ onTaskComplete }) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [isExecuting, setIsExecuting] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [agentProgress, setAgentProgress] = useState<AgentProgress[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState('Planning');
  const [executionLog, setExecutionLog] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const phases = ['Planning', 'Research', 'Analysis', 'Creation', 'Coordination', 'Completion'];

  const executeTask = async () => {
    if (!taskDescription.trim()) {
      setError('Please enter a task description');
      return;
    }

    setIsExecuting(true);
    setError(null);
    setExecutionLog([]);
    setAgentProgress([]);
    setOverallProgress(0);

    try {
      // Initialize agents
      const initialAgents: AgentProgress[] = [
        { name: 'Task Planner', status: AgentStatus.PLANNING, progress: 0, output: 'Initializing...', confidence: 0 },
        { name: 'Research Agent', status: AgentStatus.PLANNING, progress: 0, output: 'Waiting...', confidence: 0 },
        { name: 'Data Analyst', status: AgentStatus.PLANNING, progress: 0, output: 'Waiting...', confidence: 0 },
        { name: 'Content Creator', status: AgentStatus.PLANNING, progress: 0, output: 'Waiting...', confidence: 0 },
        { name: 'Task Coordinator', status: AgentStatus.PLANNING, progress: 0, output: 'Waiting...', confidence: 0 }
      ];
      setAgentProgress(initialAgents);

      // Start task execution
      const response = await fetch('/api/v1/tasks/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: taskDescription,
          priority: priority
        })
      });

      if (!response.ok) {
        throw new Error('Task execution failed');
      }

      const result: TaskResult = await response.json();
      setTaskId(result.task_id);
      
      // Simulate real-time progress updates
      await simulateExecutionProgress(result);
      
      onTaskComplete(result);
      setIsExecuting(false);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Task execution failed');
      setIsExecuting(false);
    }
  };

  const simulateExecutionProgress = async (result: TaskResult) => {
    // Phase 1: Planning (0-20%)
    await updatePhaseProgress('Planning', 0, 20, 0);
    
    // Phase 2: Research (20-40%)
    await updatePhaseProgress('Research', 20, 40, 1);
    
    // Phase 3: Analysis (40-60%)
    await updatePhaseProgress('Analysis', 40, 60, 2);
    
    // Phase 4: Creation (60-80%)
    await updatePhaseProgress('Creation', 60, 80, 3);
    
    // Phase 5: Coordination (80-95%)
    await updatePhaseProgress('Coordination', 80, 95, 4);
    
    // Phase 6: Completion (95-100%)
    await updatePhaseProgress('Completion', 95, 100, 4);
  };

  const updatePhaseProgress = async (phase: string, startProgress: number, endProgress: number, agentIndex: number) => {
    setCurrentPhase(phase);
    
    for (let progress = startProgress; progress <= endProgress; progress += 2) {
      setOverallProgress(progress);
      
      // Update agent progress
      if (agentIndex < agentProgress.length) {
        const updatedAgents = [...agentProgress];
        updatedAgents[agentIndex] = {
          ...updatedAgents[agentIndex],
          status: progress >= endProgress ? AgentStatus.COMPLETED : AgentStatus.EXECUTING,
          progress: Math.min(100, ((progress - startProgress) / (endProgress - startProgress)) * 100),
          output: getAgentOutput(phase, progress, endProgress),
          confidence: Math.min(0.9, 0.3 + (progress - startProgress) / (endProgress - startProgress) * 0.6)
        };
        setAgentProgress(updatedAgents);
      }
      
      // Add execution log entry
      if (progress % 10 === 0) {
        setExecutionLog(prev => [...prev, `${phase}: ${progress}% complete`]);
      }
      
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  };

  const getAgentOutput = (phase: string, progress: number, maxProgress: number): string => {
    const phaseOutputs = {
      'Planning': [
        'Analyzing task requirements...',
        'Breaking down into subtasks...',
        'Creating execution plan...',
        'Selecting appropriate agents...',
        'Planning phase completed'
      ],
      'Research': [
        'Gathering information...',
        'Searching knowledge base...',
        'Analyzing context...',
        'Identifying knowledge gaps...',
        'Research phase completed'
      ],
      'Analysis': [
        'Processing data...',
        'Running analysis...',
        'Generating insights...',
        'Evaluating results...',
        'Analysis phase completed'
      ],
      'Creation': [
        'Creating content...',
        'Generating reports...',
        'Building visualizations...',
        'Finalizing output...',
        'Creation phase completed'
      ],
      'Coordination': [
        'Coordinating agents...',
        'Quality assurance...',
        'Final review...',
        'Preparing delivery...',
        'Coordination completed'
      ],
      'Completion': [
        'Finalizing results...',
        'Quality check...',
        'Task completed successfully'
      ]
    };
    
    const outputs = phaseOutputs[phase as keyof typeof phaseOutputs] || ['Processing...'];
    const outputIndex = Math.floor((progress / maxProgress) * (outputs.length - 1));
    return outputs[Math.min(outputIndex, outputs.length - 1)];
  };

  const getStatusColor = (status: AgentStatus): string => {
    switch (status) {
      case AgentStatus.COMPLETED: return 'text-green-600';
      case AgentStatus.EXECUTING: return 'text-blue-600';
      case AgentStatus.FAILED: return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: AgentStatus): string => {
    switch (status) {
      case AgentStatus.COMPLETED: return '✅';
      case AgentStatus.EXECUTING: return '🔄';
      case AgentStatus.FAILED: return '❌';
      default: return '⏳';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Enhanced Task Execution</h2>
      
      {/* Task Input */}
      <div className="mb-8 p-6 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Task Description
            </label>
            <textarea
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              placeholder="Describe your task in detail (e.g., 'Analyze Q3 financial performance and create a trend chart')"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              disabled={isExecuting}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isExecuting}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={executeTask}
          disabled={isExecuting || !taskDescription.trim()}
          className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isExecuting ? 'Executing...' : 'Execute Task'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Execution Progress */}
      {isExecuting && (
        <div className="space-y-6">
          {/* Overall Progress */}
          <div className="p-6 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-blue-800">Overall Progress</h3>
              <span className="text-blue-600 font-medium">{overallProgress.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
            <p className="mt-2 text-blue-700">Current Phase: {currentPhase}</p>
          </div>

          {/* Phase Progress */}
          <div className="p-6 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Phase Progress</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {phases.map((phase, index) => {
                const phaseProgress = Math.min(100, Math.max(0, 
                  ((overallProgress - (index * 16.67)) / 16.67) * 100
                ));
                const isActive = currentPhase === phase;
                const isCompleted = overallProgress > (index + 1) * 16.67;
                
                return (
                  <div key={phase} className="text-center">
                    <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center text-lg font-bold ${
                      isCompleted ? 'bg-green-500 text-white' :
                      isActive ? 'bg-blue-500 text-white' :
                      'bg-gray-300 text-gray-600'
                    }`}>
                      {isCompleted ? '✓' : index + 1}
                    </div>
                    <p className={`text-xs font-medium ${
                      isActive ? 'text-blue-600' : 
                      isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {phase}
                    </p>
                    {isActive && (
                      <p className="text-xs text-blue-600 mt-1">
                        {phaseProgress.toFixed(0)}%
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Agent Progress */}
          <div className="p-6 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Agent Progress</h3>
            <div className="space-y-4">
              {agentProgress.map((agent, index) => (
                <div key={index} className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{getStatusIcon(agent.status)}</span>
                      <span className="font-medium text-gray-800">{agent.name}</span>
                    </div>
                    <div className="text-right">
                      <span className={`text-sm font-medium ${getStatusColor(agent.status)}`}>
                        {agent.status}
                      </span>
                      <div className="text-xs text-gray-500">
                        Confidence: {(agent.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${agent.progress}%` }}
                    />
                  </div>
                  
                  <p className="text-sm text-gray-600">{agent.output}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Execution Log */}
          <div className="p-6 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Execution Log</h3>
            <div className="bg-white p-4 rounded-lg border border-gray-200 max-h-48 overflow-y-auto">
              {executionLog.length > 0 ? (
                <div className="space-y-1">
                  {executionLog.map((log, index) => (
                    <div key={index} className="text-sm text-gray-600 font-mono">
                      [{new Date().toLocaleTimeString()}] {log}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Waiting for execution to begin...</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Task ID Display */}
      {taskId && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-800">
            <span className="font-medium">Task ID:</span> {taskId}
          </p>
        </div>
      )}
    </div>
  );
};

export default EnhancedTaskExecution;
