import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import {
  BuildingOfficeIcon,
  ChartBarIcon,
  NewspaperIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import ContradictionBadge from '../components/ContradictionBadge';

const CompanyDetail = () => {
  const { companyName } = useParams();

  // Fetch company stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['companyStats', companyName],
    queryFn: () => apiService.getCompanyStats(companyName),
    select: (response) => response.data
  });

  // Fetch company news
  const { data: news, isLoading: newsLoading } = useQuery({
    queryKey: ['companyNews', companyName],
    queryFn: () => apiService.getCompanyNews(companyName, 10),
    select: (response) => response.data
  });

  // Fetch company analyses
  const { data: analyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['companyAnalyses', companyName],
    queryFn: () => apiService.getCompanyAnalyses(companyName, 5),
    select: (response) => response.data
  });

  if (statsLoading) {
    return (
      <div className="flex justify-center items-center" style={{ height: '16rem' }}>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <BuildingOfficeIcon style={{ height: '3rem', width: '3rem', color: '#6b7280', marginRight: '1rem' }} />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  {companyName}
                </h1>
                <p className="text-sm text-gray-500">
                  Company monitoring dashboard
                </p>
              </div>
            </div>
            {stats?.latest_contradiction_level && (
              <ContradictionBadge level={stats.latest_contradiction_level} size="lg" />
            )}
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4" style={{ gap: '1.25rem' }}>
        <div className="card">
          <div className="card-body text-center">
            <DocumentTextIcon style={{ height: '2rem', width: '2rem', color: '#6b7280', margin: '0 auto', marginBottom: '0.5rem' }} />
            <div className="text-2xl font-bold text-gray-900">
              {stats?.document_count || 0}
            </div>
            <div className="text-sm text-gray-500">Documents</div>
          </div>
        </div>

        <div className="card">
          <div className="card-body text-center">
            <NewspaperIcon style={{ height: '2rem', width: '2rem', color: '#6b7280', margin: '0 auto', marginBottom: '0.5rem' }} />
            <div className="text-2xl font-bold text-gray-900">
              {stats?.news_count || 0}
            </div>
            <div className="text-sm text-gray-500">News Articles</div>
          </div>
        </div>

        <div className="card">
          <div className="card-body text-center">
            <ChartBarIcon style={{ height: '2rem', width: '2rem', color: '#6b7280', margin: '0 auto', marginBottom: '0.5rem' }} />
            <div className="text-2xl font-bold text-gray-900">
              {stats?.analysis_count || 0}
            </div>
            <div className="text-sm text-gray-500">Analyses</div>
          </div>
        </div>

        <div className="card">
          <div className="card-body text-center">
            <div style={{
              height: '2rem',
              width: '2rem',
              borderRadius: '50%',
              margin: '0 auto',
              marginBottom: '0.5rem',
              backgroundColor: stats?.latest_contradiction_level === 'HIGH' ? '#dc2626' :
                stats?.latest_contradiction_level === 'MEDIUM' ? '#ea580c' :
                stats?.latest_contradiction_level === 'LOW' ? '#ca8a04' : '#16a34a'
            }} />
            <div className="text-2xl font-bold text-gray-900">
              {stats?.latest_contradiction_level || 'NONE'}
            </div>
            <div className="text-sm text-gray-500">Risk Level</div>
          </div>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Recent News */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent News</h2>
          </div>
          <div className="card-body">
            {newsLoading ? (
              <LoadingSpinner />
            ) : news?.length === 0 ? (
              <p className="text-gray-500 text-center" style={{ padding: '2rem' }}>
                No recent news found
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {news?.slice(0, 5).map((article) => (
                  <div key={article.id} style={{
                    padding: '0.75rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    borderLeft: `4px solid ${
                      article.severity === 'HIGH' ? '#dc2626' :
                      article.severity === 'MEDIUM' ? '#ea580c' : '#ca8a04'
                    }`
                  }}>
                    <div className="flex justify-between items-start" style={{ marginBottom: '0.5rem' }}>
                      <span className={`badge badge-${article.severity?.toLowerCase()}`}>
                        {article.severity}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(article.published_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h4 className="text-sm font-medium text-gray-900" style={{ marginBottom: '0.25rem' }}>
                      {article.title}
                    </h4>
                    <p className="text-sm text-gray-600" style={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {article.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Analyses</h2>
          </div>
          <div className="card-body">
            {analysesLoading ? (
              <LoadingSpinner />
            ) : analyses?.length === 0 ? (
              <p className="text-gray-500 text-center" style={{ padding: '2rem' }}>
                No analyses found
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {analyses?.map((analysis) => (
                  <div key={analysis.id} style={{
                    padding: '0.75rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem'
                  }}>
                    <div className="flex justify-between items-start" style={{ marginBottom: '0.5rem' }}>
                      <ContradictionBadge
                        level={analysis.contradiction_level}
                        confidence={analysis.confidence_score}
                      />
                      <span className="text-xs text-gray-500">
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {analysis.query && (
                      <h4 className="text-sm font-medium text-gray-900" style={{ marginBottom: '0.25rem' }}>
                        Query: {analysis.query}
                      </h4>
                    )}
                    <p className="text-sm text-gray-600" style={{
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {analysis.analysis}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyDetail;