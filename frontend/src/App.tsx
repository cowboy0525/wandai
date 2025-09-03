/**
 * Wand AI - Main Application Component
 * Senior-Level Implementation with Professional Architecture
 */

import React, { useState, useEffect } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ThemeProvider, ThemeToggle } from './contexts/ThemeContext';
import LoadingSpinner, { LoadingStates } from './components/ui/LoadingSpinner';
import { apiService } from './services/api';
import { cn } from './utils/cn';

// Import components
import DocumentUpload from './components/DocumentUpload';
import EnhancedKnowledgeSearch from './components/EnhancedKnowledgeSearch';
import EnhancedTaskExecution from './components/EnhancedTaskExecution';
import EnhancedDashboard from './components/EnhancedDashboard';
import TaskStatus from './components/TaskStatus';

// Types
type TabType = 'dashboard' | 'upload' | 'search' | 'execute' | 'status';

interface AppState {
  activeTab: TabType;
  currentTaskId: string | null;
  isOnline: boolean;
  lastOnlineCheck: Date;
}

// Main App Component
const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    activeTab: 'dashboard',
    currentTaskId: null,
    isOnline: true,
    lastOnlineCheck: new Date(),
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check system health on mount
  useEffect(() => {
    const checkSystemHealth = async (): Promise<void> => {
      try {
        setIsLoading(true);
        setError(null);

        // Check backend health
        const isHealthy = await apiService.healthCheck();
        
        if (!isHealthy) {
          setError('Backend service is not responding. Please check if the server is running.');
        }

        // Check online status
        const onlineStatus = navigator.onLine;
        setAppState(prev => ({
          ...prev,
          isOnline: onlineStatus,
          lastOnlineCheck: new Date(),
        }));

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to check system health';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    checkSystemHealth();

    // Set up online/offline listeners
    const handleOnline = (): void => {
      setAppState(prev => ({ ...prev, isOnline: true }));
    };

    const handleOffline = (): void => {
      setAppState(prev => ({ ...prev, isOnline: false }));
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Event handlers
  const handleTaskCreated = (taskId: string): void => {
    setAppState(prev => ({
      ...prev,
      currentTaskId: taskId,
      activeTab: 'status',
    }));
  };

  const handleSearchComplete = (results: any[], suggestions: any[]): void => {
    console.log('Search completed:', results.length, 'results,', suggestions.length, 'suggestions');
    // Could show results in dashboard or trigger notifications
  };

  const handleTabChange = (tab: TabType): void => {
    setAppState(prev => ({ ...prev, activeTab: tab }));
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <LoadingSpinner size="xl" text="Initializing Wand AI..." />
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="text-center">
            <div className="text-red-600 text-6xl mb-4">⚠️</div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              System Initialization Failed
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main app content
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                <span className="text-blue-600 dark:text-blue-400">Wand</span> AI
              </h1>
              <span className="ml-3 text-sm text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
                Enhanced Multi-Agent System
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Online Status Indicator */}
              <div className={cn(
                'flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium',
                appState.isOnline
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              )}>
                <div className={cn(
                  'w-2 h-2 rounded-full',
                  appState.isOnline ? 'bg-green-500' : 'bg-red-500'
                )} />
                <span>{appState.isOnline ? 'Online' : 'Offline'}</span>
              </div>

              {/* Theme Toggle */}
              <ThemeToggle size="md" showLabel={false} />
              
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Enterprise AI Workforce
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
              { id: 'upload', label: '📄 Document Upload', icon: '📄' },
              { id: 'search', label: '🔍 Enhanced Search', icon: '🔍' },
              { id: 'execute', label: '🤖 Enhanced Tasks', icon: '🤖' },
              { id: 'status', label: '📈 Task Status', icon: '📈' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id as TabType)}
                className={cn(
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
                  appState.activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LoadingStates
          loading={isLoading}
          error={error}
          loadingComponent={
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" text="Loading..." />
            </div>
          }
        >
          {/* Tab Content */}
          {appState.activeTab === 'dashboard' && (
            <EnhancedDashboard
              recentTasks={[]}
              recentSearches={[]}
              recentSuggestions={[]}
            />
          )}
          
          {appState.activeTab === 'upload' && (
            <DocumentUpload />
          )}
          
          {appState.activeTab === 'search' && (
            <EnhancedKnowledgeSearch onSearchComplete={handleSearchComplete} />
          )}
          
                     {appState.activeTab === 'execute' && (
             <EnhancedTaskExecution onTaskComplete={(result) => handleTaskCreated(result.task_id)} />
           )}
          
          {appState.activeTab === 'status' && (
            <TaskStatus taskId={appState.currentTaskId} />
          )}
        </LoadingStates>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500 dark:text-gray-400">
            <p>© 2024 Wand AI. Enterprise AI Workforce Platform.</p>
            <p className="mt-1">
              Last online check: {appState.lastOnlineCheck.toLocaleTimeString()}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Wrapped App with Error Boundary and Theme Provider
const AppWithProviders: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default AppWithProviders;
