import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface SearchResult {
  document_id: string;
  filename: string;
  content: string;
  relevance_score: number;
  page_number?: number;
}

interface EnrichmentSuggestion {
  type: string;
  description: string;
  priority: string;
  source?: string;
}

const KnowledgeSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<EnrichmentSuggestion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearching(true);
    setError(null);
    setResults([]);
    setSuggestions([]);

    try {
      const response = await axios.post('/search', { query: query.trim() });
      setResults(response.data.results || []);
      setSuggestions(response.data.suggestions || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setSearching(false);
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

  const formatRelevanceScore = (score: number): string => {
    const percentage = Math.round(score * 100);
    if (percentage >= 80) return 'Very High';
    if (percentage >= 60) return 'High';
    if (percentage >= 40) return 'Medium';
    if (percentage >= 20) return 'Low';
    return 'Very Low';
  };

  const getRelevanceColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-blue-600 bg-blue-100';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100';
    if (score >= 0.2) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string): string => {
    switch (type.toLowerCase()) {
      case 'document':
        return '📄';
      case 'data':
        return '📊';
      case 'action':
        return '⚡';
      default:
        return '💡';
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Knowledge Base
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                id="search-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question or search for information..."
                className="flex-1 rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500 focus:outline-none"
                disabled={searching}
              />
              <button
                type="submit"
                disabled={searching || !query.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed btn-primary"
              >
                {searching ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Searching...</span>
                  </div>
                ) : (
                  '🔍 Search'
                )}
              </button>
            </div>
          </div>
          
          <div className="text-sm text-gray-500">
            <p>💡 <strong>Tip:</strong> Ask questions in natural language. The system will search through your uploaded documents and provide relevant answers.</p>
          </div>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="text-red-400">⚠️</div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Search Results ({results.length})
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Found {results.length} relevant document sections
            </p>
          </div>
          
          <div className="divide-y divide-gray-200">
            {results.map((result, index) => (
              <div key={`${result.document_id}-${index}`} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="text-2xl">📄</div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {result.filename}
                        </p>
                        {result.page_number !== undefined && (
                          <p className="text-xs text-gray-500">
                            Page {result.page_number + 1}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRelevanceColor(result.relevance_score)}`}>
                        Relevance: {formatRelevanceScore(result.relevance_score)} ({Math.round(result.relevance_score * 100)}%)
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-700">
                      {expandedResults.has(`${result.document_id}-${index}`) ? (
                        <div className="space-y-2">
                          <ReactMarkdown>{result.content}</ReactMarkdown>
                          <button
                            onClick={() => toggleResultExpansion(`${result.document_id}-${index}`)}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            Show less
                          </button>
                        </div>
                      ) : (
                        <div>
                          <p className="line-clamp-3">
                            {result.content.length > 300 
                              ? `${result.content.substring(0, 300)}...` 
                              : result.content
                            }
                          </p>
                          {result.content.length > 300 && (
                            <button
                              onClick={() => toggleResultExpansion(`${result.document_id}-${index}`)}
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-2"
                            >
                              Read more
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enrichment Suggestions */}
      {suggestions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Knowledge Enrichment Suggestions
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Improve your knowledge base with these recommendations
            </p>
          </div>
          
          <div className="p-6">
            <div className="grid gap-4 md:grid-cols-2">
              {suggestions.map((suggestion, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors card-hover">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">{getTypeIcon(suggestion.type)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(suggestion.priority)}`}>
                          {suggestion.priority}
                        </span>
                        <span className="text-xs text-gray-500 capitalize">
                          {suggestion.type}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-900 mb-2">
                        {suggestion.description}
                      </p>
                      
                      {suggestion.source && (
                        <p className="text-xs text-gray-500">
                          Source: {suggestion.source}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!searching && results.length === 0 && suggestions.length === 0 && query && !error && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-500">
            Try adjusting your search terms or upload more documents to expand your knowledge base.
          </p>
        </div>
      )}
    </div>
  );
};

export default KnowledgeSearch;
