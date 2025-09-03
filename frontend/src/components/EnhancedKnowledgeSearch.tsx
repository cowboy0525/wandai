import React, { useState } from 'react';
import { SearchQuery, SearchResult, EnrichmentSuggestion } from '../types';

interface EnhancedKnowledgeSearchProps {
  onSearchComplete: (results: SearchResult[], suggestions: EnrichmentSuggestion[]) => void;
}

interface SearchMetrics {
  overallConfidence: number;
  coverageScore: number;
  knowledgeGaps: string[];
  enrichmentSuggestions: EnrichmentSuggestion[];
}

const EnhancedKnowledgeSearch: React.FC<EnhancedKnowledgeSearchProps> = ({ onSearchComplete }) => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchMetrics, setSearchMetrics] = useState<SearchMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const executeSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResults([]);
    setSearchMetrics(null);

    try {
      const response = await fetch('/api/v1/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      
      setSearchResults(data.results || []);
      
      // Extract metrics from enhanced search response
      const metrics: SearchMetrics = {
        overallConfidence: data.overall_confidence || 0.5,
        coverageScore: data.completeness_analysis?.coverage_score || 0.5,
        knowledgeGaps: data.completeness_analysis?.knowledge_gaps || [],
        enrichmentSuggestions: data.enrichment_suggestions || []
      };
      
      setSearchMetrics(metrics);
      onSearchComplete(data.results || [], data.enrichment_suggestions || []);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const getCoverageColor = (coverage: number): string => {
    if (coverage >= 0.8) return 'text-green-600';
    if (coverage >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCoverageLabel = (coverage: number): string => {
    if (coverage >= 0.8) return 'Excellent';
    if (coverage >= 0.6) return 'Good';
    if (coverage >= 0.4) return 'Fair';
    return 'Poor';
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Enhanced Knowledge Search</h2>
      
      {/* Search Input */}
      <div className="mb-8 p-6 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question or describe what you're looking for..."
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              disabled={isSearching}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Results
            </label>
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isSearching}
            >
              <option value={3}>3 results</option>
              <option value={5}>5 results</option>
              <option value={10}>10 results</option>
              <option value={15}>15 results</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={executeSearch}
            disabled={isSearching || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSearching ? 'Searching...' : 'Search Knowledge Base'}
          </button>
          
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Options
          </button>
        </div>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">Advanced Search Options</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-blue-700 mb-1">
                Search Strategy
              </label>
              <select className="w-full p-2 border border-blue-200 rounded-md text-sm">
                <option value="semantic">Semantic Search</option>
                <option value="keyword">Keyword Search</option>
                <option value="hybrid">Hybrid Search</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-blue-700 mb-1">
                Confidence Threshold
              </label>
              <select className="w-full p-2 border border-blue-200 rounded-md text-sm">
                <option value="0.5">50% (Default)</option>
                <option value="0.7">70%</option>
                <option value="0.8">80%</option>
                <option value="0.9">90%</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-blue-700 mb-1">
                Sort By
              </label>
              <select className="w-full p-2 border border-blue-200 rounded-md text-sm">
                <option value="relevance">Relevance</option>
                <option value="confidence">Confidence</option>
                <option value="date">Date</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Search Metrics */}
      {searchMetrics && (
        <div className="mb-6 space-y-4">
          {/* Overall Confidence */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-blue-800">Search Confidence</h3>
              <div className="text-right">
                <span className={`text-2xl font-bold ${getConfidenceColor(searchMetrics.overallConfidence)}`}>
                  {(searchMetrics.overallConfidence * 100).toFixed(0)}%
                </span>
                <div className={`text-sm font-medium ${getConfidenceColor(searchMetrics.overallConfidence)}`}>
                  {getConfidenceLabel(searchMetrics.overallConfidence)} Confidence
                </div>
              </div>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-3 mt-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${searchMetrics.overallConfidence * 100}%` }}
              />
            </div>
          </div>

          {/* Coverage Analysis */}
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-green-800">Knowledge Coverage</h3>
              <div className="text-right">
                <span className={`text-2xl font-bold ${getCoverageColor(searchMetrics.coverageScore)}`}>
                  {(searchMetrics.coverageScore * 100).toFixed(0)}%
                </span>
                <div className={`text-sm font-medium ${getCoverageColor(searchMetrics.coverageScore)}`}>
                  {getCoverageLabel(searchMetrics.coverageScore)} Coverage
                </div>
              </div>
            </div>
            <div className="w-full bg-green-200 rounded-full h-3 mt-3">
              <div 
                className="bg-green-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${searchMetrics.coverageScore * 100}%` }}
              />
            </div>
          </div>

          {/* Knowledge Gaps */}
          {searchMetrics.knowledgeGaps.length > 0 && (
            <div className="p-4 bg-yellow-50 rounded-lg">
              <h3 className="text-lg font-semibold text-yellow-800 mb-3">Knowledge Gaps Identified</h3>
              <div className="space-y-2">
                {searchMetrics.knowledgeGaps.map((gap, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-yellow-600">⚠️</span>
                    <span className="text-yellow-800">{gap}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-800">
            Search Results ({searchResults.length})
          </h3>
          
          {searchResults.map((result, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800 mb-1">
                    {result.filename}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">
                    {result.content_snippet}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <div className="text-sm text-gray-500 mb-1">
                    Relevance: {(result.relevance_score * 100).toFixed(0)}%
                  </div>
                  {result.metadata?.confidence && (
                    <div className="text-sm text-gray-500">
                      Confidence: {(result.metadata.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>
              
              {/* Metadata Display */}
              {result.metadata && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {result.metadata.chunk_type && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {result.metadata.chunk_type}
                    </span>
                  )}
                  {result.metadata.importance_score && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Importance: {(result.metadata.importance_score * 100).toFixed(0)}%
                    </span>
                  )}
                  {result.metadata.knowledge_areas && result.metadata.knowledge_areas.length > 0 && (
                    result.metadata.knowledge_areas.map((area: string, areaIndex: number) => (
                      <span key={areaIndex} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                        {area}
                      </span>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Enrichment Suggestions */}
      {searchMetrics?.enrichmentSuggestions && searchMetrics.enrichmentSuggestions.length > 0 && (
        <div className="mt-8 p-6 bg-purple-50 rounded-lg">
          <h3 className="text-xl font-semibold text-purple-800 mb-4">
            Knowledge Enrichment Suggestions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {searchMetrics.enrichmentSuggestions.map((suggestion, index) => (
              <div key={index} className="p-4 bg-white rounded-lg border border-purple-200">
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(suggestion.priority)}`}>
                    {suggestion.priority} Priority
                  </span>
                  <span className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                    {suggestion.suggestion_type}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-3">{suggestion.description}</p>
                {suggestion.related_queries && suggestion.related_queries.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Related queries:</p>
                    <div className="flex flex-wrap gap-1">
                      {suggestion.related_queries.map((query, queryIndex) => (
                        <span key={queryIndex} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          {query}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {!isSearching && searchResults.length === 0 && query && !error && (
        <div className="text-center py-8">
          <div className="text-gray-400 text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-600 mb-2">No results found</h3>
          <p className="text-gray-500">
            Try adjusting your search query or check the enrichment suggestions above.
          </p>
        </div>
      )}
    </div>
  );
};

export default EnhancedKnowledgeSearch;
