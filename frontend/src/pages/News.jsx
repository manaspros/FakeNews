import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import {
  NewspaperIcon,
  PlusIcon,
  ClockIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const News = () => {
  const [selectedCompany, setSelectedCompany] = useState('');
  const [showAddNews, setShowAddNews] = useState(false);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const queryClient = useQueryClient();

  // Fetch companies
  const { data: companies } = useQuery({
    queryKey: ['companies'],
    queryFn: () => apiService.getCompanies(),
    select: (response) => response.data
  });

  // Fetch news
  const { data: news, isLoading: newsLoading, refetch } = useQuery({
    queryKey: ['news', selectedCompany],
    queryFn: () => selectedCompany
      ? apiService.getCompanyNews(selectedCompany)
      : Promise.resolve({ data: [] }),
    enabled: !!selectedCompany,
    select: (response) => response.data,
    refetchInterval: 60000, // Refetch every minute
  });

  // Filter news by severity
  const filteredNews = news?.filter(article =>
    severityFilter === 'ALL' || article.severity === severityFilter
  ) || [];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'HIGH': return 'high-severity';
      case 'MEDIUM': return 'medium-severity';
      case 'LOW': return 'low-severity';
      default: return '';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'HIGH': return '🚨';
      case 'MEDIUM': return '⚠️';
      case 'LOW': return 'ℹ️';
      default: return '📰';
    }
  };

  const getTimeDifference = (publishedAt) => {
    const now = new Date();
    const published = new Date(publishedAt);
    const diffInHours = Math.floor((now - published) / (1000 * 60 * 60));

    if (diffInHours < 1) return 'Less than 1 hour ago';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} days ago`;
  };

  return (
    <div style={{ maxWidth: '96rem', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <NewspaperIcon style={{ height: '2rem', width: '2rem', color: '#2563eb', marginRight: '0.75rem' }} />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Company News Monitor
                </h1>
                <p className="text-sm text-gray-500">
                  Track news and developments for monitored companies
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowAddNews(true)}
              className="btn btn-primary"
            >
              <PlusIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
              Add News
            </button>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-3" style={{ gap: '1rem' }}>
            {/* Company Selection */}
            <div className="form-group">
              <label className="form-label">
                Select Company
              </label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="form-input form-select"
              >
                <option value="">All companies...</option>
                {companies?.map((company) => (
                  <option key={company.name} value={company.name}>
                    {company.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity Filter */}
            <div className="form-group">
              <label className="form-label">
                <FunnelIcon style={{ height: '1rem', width: '1rem', display: 'inline', marginRight: '0.25rem' }} />
                Severity Filter
              </label>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="form-input form-select"
              >
                <option value="ALL">All severities</option>
                <option value="HIGH">High severity</option>
                <option value="MEDIUM">Medium severity</option>
                <option value="LOW">Low severity</option>
              </select>
            </div>

            {/* Refresh Button */}
            <div style={{ display: 'flex', alignItems: 'flex-end' }}>
              <button
                onClick={() => refetch()}
                disabled={!selectedCompany || newsLoading}
                className="btn btn-secondary"
                style={{ width: '100%' }}
              >
                {newsLoading ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <ClockIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
                )}
                Refresh News
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* News List */}
      {selectedCompany ? (
        <div className="card">
          <div className="card-body">
            <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
              <h2 className="text-lg font-medium text-gray-900">
                News for {selectedCompany}
              </h2>
              <span className="text-sm text-gray-500">
                {filteredNews.length} articles
                {severityFilter !== 'ALL' && ` (${severityFilter.toLowerCase()} severity)`}
              </span>
            </div>

            {newsLoading ? (
              <div className="flex justify-center items-center" style={{ height: '8rem' }}>
                <LoadingSpinner />
              </div>
            ) : filteredNews.length === 0 ? (
              <div className="text-center" style={{ padding: '3rem' }}>
                <NewspaperIcon style={{ margin: '0 auto', height: '3rem', width: '3rem', color: '#9ca3af' }} />
                <h3 style={{ marginTop: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>No news found</h3>
                <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#6b7280' }}>
                  {selectedCompany ? `No news articles found for ${selectedCompany}` : 'Select a company to view news'}
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {filteredNews.map((article) => (
                  <NewsArticleCard key={article.id} article={article} />
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-body text-center">
            <NewspaperIcon style={{ margin: '0 auto', height: '3rem', width: '3rem', color: '#9ca3af' }} />
            <h3 style={{ marginTop: '0.5rem', fontSize: '1.125rem', fontWeight: '500', color: '#111827' }}>
              Select a Company
            </h3>
            <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#6b7280' }}>
              Choose a company from the dropdown to view their latest news
            </p>
          </div>
        </div>
      )}

      {/* Add News Modal */}
      {showAddNews && (
        <AddNewsModal
          companies={companies}
          onClose={() => setShowAddNews(false)}
          onSuccess={() => {
            queryClient.invalidateQueries(['news']);
            setShowAddNews(false);
          }}
        />
      )}
    </div>
  );
};

// News Article Card Component
const NewsArticleCard = ({ article }) => {
  const getSeverityBadgeClass = (severity) => {
    switch (severity) {
      case 'HIGH': return 'badge badge-high';
      case 'MEDIUM': return 'badge badge-medium';
      case 'LOW': return 'badge badge-low';
      default: return 'badge badge-gray';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'HIGH': return '🚨';
      case 'MEDIUM': return '⚠️';
      case 'LOW': return 'ℹ️';
      default: return '📰';
    }
  };

  const getTimeDifference = (publishedAt) => {
    const now = new Date();
    const published = new Date(publishedAt);
    const diffInHours = Math.floor((now - published) / (1000 * 60 * 60));

    if (diffInHours < 1) return 'Less than 1 hour ago';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} days ago`;
  };

  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '0.5rem',
      padding: '1rem',
      transition: 'background-color 0.2s'
    }}
    onMouseEnter={(e) => e.target.style.backgroundColor = '#f9fafb'}
    onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
    >
      <div className="flex justify-between items-start" style={{ marginBottom: '0.75rem' }}>
        <div className="flex items-center" style={{ gap: '0.5rem' }}>
          <span className={getSeverityBadgeClass(article.severity)}>
            {getSeverityIcon(article.severity)} {article.severity}
          </span>
          <span className="text-sm text-gray-500">{article.source}</span>
        </div>
        <span className="text-sm" style={{ color: '#9ca3af' }}>
          {getTimeDifference(article.published_at)}
        </span>
      </div>

      <h3 className="text-lg font-medium text-gray-900" style={{ marginBottom: '0.5rem' }}>
        {article.title}
      </h3>

      <p style={{ color: '#4b5563', fontSize: '0.875rem', marginBottom: '0.75rem', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
        {article.content}
      </p>

      <div className="flex justify-between items-center">
        <div className="flex items-center" style={{ gap: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
          {article.sentiment_score !== undefined && (
            <span>
              Sentiment: {article.sentiment_score > 0 ? '😊' : article.sentiment_score < 0 ? '😞' : '😐'}
              {Math.round(article.sentiment_score * 100)}%
            </span>
          )}
        </div>
        {article.url && (
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center text-sm"
            style={{ color: '#2563eb', textDecoration: 'none' }}
          >
            Read full article 
          </a>
        )}
      </div>
    </div>
  );
};

// Add News Modal Component
const AddNewsModal = ({ companies, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    company: '',
    headline: '',
    content: '',
    source: 'Manual Entry',
    severity: 'MEDIUM'
  });

  const mutation = useMutation({
    mutationFn: (data) => apiService.addNewsUpdate(data),
    onSuccess: () => {
      toast.success('News added successfully!');
      onSuccess();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to add news');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.company || !formData.headline || !formData.content) {
      toast.error('Please fill in all required fields');
      return;
    }
    mutation.mutate(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="text-lg font-medium text-gray-900">
            Add News Update
          </h3>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">
                Company *
              </label>
              <select
                value={formData.company}
                onChange={(e) => setFormData({...formData, company: e.target.value})}
                className="form-input form-select"
                required
              >
                <option value="">Select company...</option>
                {companies?.map((company) => (
                  <option key={company.name} value={company.name}>
                    {company.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                Headline *
              </label>
              <input
                type="text"
                value={formData.headline}
                onChange={(e) => setFormData({...formData, headline: e.target.value})}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Content *
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                className="form-input form-textarea"
                style={{ height: '6rem', resize: 'none' }}
                required
              />
            </div>

            <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">
                  Source
                </label>
                <input
                  type="text"
                  value={formData.source}
                  onChange={(e) => setFormData({...formData, source: e.target.value})}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Severity
                </label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({...formData, severity: e.target.value})}
                  className="form-input form-select"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
              </div>
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button
            type="button"
            onClick={onClose}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={mutation.isPending}
            className="btn btn-primary"
          >
            {mutation.isPending ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Adding...
              </>
            ) : (
              'Add News'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default News;