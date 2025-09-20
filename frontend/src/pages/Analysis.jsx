import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import {
  PlayIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import ContradictionBadge from '../components/ContradictionBadge';

const Analysis = () => {
  const [selectedCompany, setSelectedCompany] = useState('');
  const [query, setQuery] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const queryClient = useQueryClient();

  // Fetch companies
  const { data: companies, isLoading: companiesLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: () => apiService.getCompanies(),
    select: (response) => response.data
  });

  // Analysis mutation
  const analysisMutation = useMutation({
    mutationFn: (data) => apiService.analyzeCompany(data),
    onSuccess: (response) => {
      setAnalysisResult(response.data);
      toast.success('Analysis completed successfully!');
      queryClient.invalidateQueries(['companyStats', selectedCompany]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Analysis failed');
    }
  });

  const handleAnalysis = (e) => {
    e.preventDefault();
    if (!selectedCompany) {
      toast.error('Please select a company');
      return;
    }

    analysisMutation.mutate({
      company: selectedCompany,
      query: query.trim()
    });
  };

  const predefinedQueries = [
    'Environmental sustainability and climate commitments',
    'Employee treatment and workplace diversity',
    'Business ethics and transparency',
    'Community involvement and social responsibility',
    'Data privacy and security practices',
    'Supply chain and labor practices'
  ];

  if (companiesLoading) {
    return (
      <div className="flex justify-center items-center" style={{ height: '16rem' }}>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '64rem', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center">
            <ExclamationTriangleIcon style={{ height: '2rem', width: '2rem', color: '#dc2626', marginRight: '0.75rem' }} />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Contradiction Analysis
              </h1>
              <p className="text-sm text-gray-500">
                Analyze companies for contradictions between stated values and actual actions
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Form */}
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleAnalysis} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Company Selection */}
            <div className="form-group">
              <label className="form-label">
                Select Company
              </label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="form-input form-select"
                required
              >
                <option value="">Choose a company...</option>
                {companies?.map((company) => (
                  <option key={company.name} value={company.name}>
                    {company.name} - {company.industry}
                  </option>
                ))}
              </select>
            </div>

            {/* Query Input */}
            <div className="form-group">
              <label className="form-label">
                Analysis Focus (Optional)
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What aspect would you like to analyze? (e.g., environmental practices, employee treatment)"
                className="form-input form-textarea"
                style={{ height: '5rem', resize: 'none' }}
              />
              <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#6b7280' }}>
                Leave blank for general analysis, or specify a focus area
              </p>
            </div>

            {/* Predefined Queries */}
            <div className="form-group">
              <label className="form-label">
                Or choose a predefined analysis:
              </label>
              <div className="grid grid-cols-2" style={{ gap: '0.5rem' }}>
                {predefinedQueries.map((predefinedQuery) => (
                  <button
                    key={predefinedQuery}
                    type="button"
                    onClick={() => setQuery(predefinedQuery)}
                    style={{
                      textAlign: 'left',
                      padding: '0.75rem',
                      fontSize: '0.875rem',
                      border: '1px solid #e5e7eb',
                      borderRadius: '0.5rem',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = '#f9fafb';
                      e.target.style.borderColor = '#d1d5db';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = 'white';
                      e.target.style.borderColor = '#e5e7eb';
                    }}
                  >
                    {predefinedQuery}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={!selectedCompany || analysisMutation.isPending}
                className="btn btn-danger btn-lg"
              >
                {analysisMutation.isPending ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <PlayIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
                    Run Analysis
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="card">
          <div className="card-body">
            <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
              <h2 className="text-xl font-bold text-gray-900">
                Analysis Results
              </h2>
              <div className="text-sm text-gray-500">
                {new Date(analysisResult.timestamp * 1000).toLocaleString()}
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-3" style={{ gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ backgroundColor: '#f9fafb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center' }}>
                <div className="text-sm font-medium text-gray-500" style={{ marginBottom: '0.25rem' }}>
                  Company
                </div>
                <div className="text-lg font-bold text-gray-900">
                  {analysisResult.company}
                </div>
              </div>

              <div style={{ backgroundColor: '#f9fafb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center' }}>
                <div className="text-sm font-medium text-gray-500" style={{ marginBottom: '0.25rem' }}>
                  Contradiction Level
                </div>
                <ContradictionBadge
                  level={analysisResult.contradiction_level}
                  confidence={analysisResult.confidence_score}
                />
              </div>

              <div style={{ backgroundColor: '#f9fafb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center' }}>
                <div className="text-sm font-medium text-gray-500" style={{ marginBottom: '0.25rem' }}>
                  Confidence Score
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(analysisResult.confidence_score * 100)}%
                </div>
              </div>
            </div>

            {/* Query Focus */}
            {analysisResult.query && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 className="text-lg font-medium text-gray-900" style={{ marginBottom: '0.5rem' }}>
                  Analysis Focus
                </h3>
                <div style={{
                  backgroundColor: '#eff6ff',
                  border: '1px solid #bfdbfe',
                  borderRadius: '0.5rem',
                  padding: '0.75rem'
                }}>
                  <p style={{ fontSize: '0.875rem', color: '#1e40af' }}>
                    {analysisResult.query}
                  </p>
                </div>
              </div>
            )}

            {/* Analysis Details */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 className="text-lg font-medium text-gray-900" style={{ marginBottom: '0.75rem' }}>
                Detailed Analysis
              </h3>
              <div style={{
                backgroundColor: '#f9fafb',
                borderRadius: '0.5rem',
                padding: '1rem'
              }}>
                <p style={{ color: '#374151', whiteSpace: 'pre-wrap' }}>
                  {analysisResult.analysis}
                </p>
              </div>
            </div>

            {/* Key Contradictions */}
            {analysisResult.key_contradictions && analysisResult.key_contradictions.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 className="text-lg font-medium text-gray-900" style={{ marginBottom: '0.75rem' }}>
                  Key Contradictions Found
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {analysisResult.key_contradictions.map((contradiction, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      padding: '0.75rem',
                      backgroundColor: '#fef2f2',
                      border: '1px solid #fecaca',
                      borderRadius: '0.5rem'
                    }}>
                      <ExclamationTriangleIcon style={{
                        height: '1.25rem',
                        width: '1.25rem',
                        color: '#dc2626',
                        marginTop: '0.125rem',
                        flexShrink: 0
                      }} />
                      <p style={{ fontSize: '0.875rem', color: '#991b1b' }}>{contradiction}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex" style={{ gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => setAnalysisResult(null)}
                className="btn btn-secondary"
              >
                New Analysis
              </button>
              <button
                onClick={() => {
                  const data = JSON.stringify(analysisResult, null, 2);
                  const blob = new Blob([data], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `analysis-${analysisResult.company}-${Date.now()}.json`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }}
                className="btn btn-primary"
              >
                Download Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Tips */}
      <div style={{
        backgroundColor: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '0.5rem',
        padding: '1rem'
      }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: '#1e40af', marginBottom: '0.5rem' }}>
          💡 Analysis Tips
        </h3>
        <ul style={{ fontSize: '0.875rem', color: '#1e40af', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <li>• Be specific in your query for more targeted results</li>
          <li>• The AI compares company documents with recent news and actions</li>
          <li>• Higher confidence scores indicate more reliable analysis</li>
          <li>• Results are saved and can be tracked over time</li>
        </ul>
      </div>
    </div>
  );
};

export default Analysis;