import React, { useState } from 'react';
import axios from 'axios';

interface TaskExecutionProps {
  onTaskCreated: (taskId: string) => void;
}

const TaskExecution: React.FC<TaskExecutionProps> = ({ onTaskCreated }) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exampleTasks] = useState([
    "Analyze our Q3 financial data and create a trend report with recommendations",
    "Summarize customer feedback from the last quarter and identify key improvement areas",
    "Create a competitive analysis report based on our market research documents",
    "Generate a quarterly performance summary with charts and insights",
    "Analyze our product documentation and suggest improvements for user experience"
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskDescription.trim()) return;

    setExecuting(true);
    setError(null);

    try {
      const response = await axios.post('/execute-task', {
        description: taskDescription.trim(),
        priority: priority
      });

      // Extract task ID from response
      const taskId = response.data.task_id || 'unknown';
      onTaskCreated(taskId);
      
      // Reset form
      setTaskDescription('');
      setPriority('medium');
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Task execution failed');
    } finally {
      setExecuting(false);
    }
  };

  const selectExampleTask = (example: string) => {
    setTaskDescription(example);
  };

  return (
    <div className="space-y-6">
      {/* Task Submission Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="task-description" className="block text-sm font-medium text-gray-700 mb-2">
              Task Description
            </label>
            <textarea
              id="task-description"
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              placeholder="Describe your business task in natural language..."
              rows={4}
              className="w-full rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500 focus:outline-none resize-none"
              disabled={executing}
            />
            <p className="text-sm text-gray-500 mt-1">
              Be specific about what you want to accomplish. The AI agents will break this down into subtasks.
            </p>
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
              Priority Level
            </label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500 focus:outline-none"
              disabled={executing}
            >
              <option value="low">Low - Normal priority</option>
              <option value="medium">Medium - Standard priority</option>
              <option value="high">High - Urgent priority</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={executing || !taskDescription.trim()}
              className="px-8 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed btn-primary text-lg font-medium"
            >
              {executing ? (
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Executing Task...</span>
                </div>
              ) : (
                '🚀 Execute Task with AI Agents'
              )}
            </button>

            {executing && (
              <div className="text-sm text-gray-500">
                <p>🤖 AI agents are planning and executing your task...</p>
              </div>
            )}
          </div>
        </form>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <div className="text-red-400">⚠️</div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Example Tasks */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          💡 Example Tasks
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Click on any example below to see how to structure your task requests:
        </p>
        
        <div className="grid gap-3 md:grid-cols-2">
          {exampleTasks.map((example, index) => (
            <button
              key={index}
              onClick={() => selectExampleTask(example)}
              className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm text-gray-700"
            >
              <div className="flex items-start space-x-3">
                <div className="text-blue-500 text-lg">📋</div>
                <div>
                  <p className="font-medium text-gray-900 mb-1">Example {index + 1}</p>
                  <p className="text-gray-600 leading-relaxed">{example}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-4">
          🔍 How Multi-Agent Task Execution Works
        </h3>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                1
              </div>
              <div>
                <p className="font-medium text-blue-900">Task Analysis</p>
                <p className="text-sm text-blue-700">The system analyzes your request and searches the knowledge base for relevant context</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                2
              </div>
              <div>
                <p className="font-medium text-blue-900">Agent Planning</p>
                <p className="text-sm text-blue-700">Specialized AI agents create a detailed execution plan</p>
              </div>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                3
              </div>
              <div>
                <p className="font-medium text-blue-900">Parallel Execution</p>
                <p className="text-sm text-blue-700">Multiple agents work simultaneously on different subtasks</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                4
              </div>
              <div>
                <p className="font-medium text-blue-900">Result Aggregation</p>
                <p className="text-sm text-blue-700">All agent outputs are combined into a comprehensive final result</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-white rounded-lg border border-blue-200">
          <h4 className="font-medium text-blue-900 mb-2">🤖 Available AI Agents:</h4>
          <div className="grid gap-2 md:grid-cols-2 text-sm text-blue-700">
            <div>• <strong>Research Agent:</strong> Gathers and analyzes information</div>
            <div>• <strong>Data Analyst:</strong> Processes data and generates insights</div>
            <div>• <strong>Content Creator:</strong> Creates reports and presentations</div>
            <div>• <strong>Task Coordinator:</strong> Manages workflow and dependencies</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskExecution;
