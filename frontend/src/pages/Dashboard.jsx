import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import {
  ExclamationTriangleIcon,
  ChartBarIcon,
  NewspaperIcon,
  BuildingOfficeIcon,
  EyeIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import ContradictionBadge from '../components/ContradictionBadge';

const Dashboard = () => {
  const [selectedCompany, setSelectedCompany] = useState('');

  // Fetch companies
  const { data: companies, isLoading: companiesLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: () => apiService.getCompanies(),
    select: (response) => response.data
  });

  // Fetch alerts
  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => apiService.getAlerts(),
    select: (response) => response.data,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch company stats for selected company
  const { data: companyStats } = useQuery({
    queryKey: ['companyStats', selectedCompany],
    queryFn: () => apiService.getCompanyStats(selectedCompany),
    enabled: !!selectedCompany,
    select: (response) => response.data
  });

  const getAlertIcon = (level) => {
    if (level === 'HIGH') return '🚨';
    if (level === 'MEDIUM') return '⚠️';
    return 'ℹ️';
  };

  if (companiesLoading) {
    return (
      <div className="flex justify-center items-center" style={{ height: '16rem' }}>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Corporate Hypocrisy Detector
              </h1>
              <p className="text-sm text-gray-500" style={{ marginTop: '0.25rem' }}>
                Real-time analysis of corporate promises vs actions
              </p>
            </div>
            <div className="flex items-center" style={{ gap: '1rem' }}>
              <ExclamationTriangleIcon style={{ height: '3rem', width: '3rem', color: '#dc2626' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4" style={{ gap: '1.25rem' }}>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div style={{ marginRight: '1.25rem' }}>
                <BuildingOfficeIcon style={{ height: '1.5rem', width: '1.5rem', color: '#9ca3af' }} />
              </div>
              <div style={{ flex: 1 }}>
                <dt className="text-sm font-medium text-gray-500">
                  Companies Monitored
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {companies?.length || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div style={{ marginRight: '1.25rem' }}>
                <ExclamationTriangleIcon style={{ height: '1.5rem', width: '1.5rem', color: '#f87171' }} />
              </div>
              <div style={{ flex: 1 }}>
                <dt className="text-sm font-medium text-gray-500">
                  Active Alerts
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {alerts?.length || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div style={{ marginRight: '1.25rem' }}>
                <ChartBarIcon style={{ height: '1.5rem', width: '1.5rem', color: '#60a5fa' }} />
              </div>
              <div style={{ flex: 1 }}>
                <dt className="text-sm font-medium text-gray-500">
                  Analyses Today
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {companyStats?.analysis_count || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div style={{ marginRight: '1.25rem' }}>
                <NewspaperIcon style={{ height: '1.5rem', width: '1.5rem', color: '#34d399' }} />
              </div>
              <div style={{ flex: 1 }}>
                <dt className="text-sm font-medium text-gray-500">
                  News Articles
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {companyStats?.news_count || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        {/* Companies List */}
        <div className="card">
          <div className="card-body">
            <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
              <h3 className="text-lg font-medium text-gray-900">
                Monitored Companies
              </h3>
              <Link
                to="/settings"
                className="btn btn-primary btn-sm"
              >
                <PlusIcon style={{ height: '1rem', width: '1rem', marginRight: '0.25rem' }} />
                Add Company
              </Link>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {companies?.map((company) => (
                <CompanyCard
                  key={company.name}
                  company={company}
                  onClick={() => setSelectedCompany(company.name)}
                  isSelected={selectedCompany === company.name}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="card">
          <div className="card-body">
            <h3 className="text-lg font-medium text-gray-900" style={{ marginBottom: '1rem' }}>
              Recent Alerts
            </h3>

            {alertsLoading ? (
              <LoadingSpinner size="sm" />
            ) : alerts?.length === 0 ? (
              <p className="text-sm text-gray-500">No alerts</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {alerts?.slice(0, 5).map((alert) => (
                  <div
                    key={alert.id}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      padding: '0.75rem',
                      backgroundColor: '#f9fafb',
                      borderRadius: '0.5rem'
                    }}
                  >
                    <span style={{ fontSize: '1.125rem' }}>
                      {getAlertIcon(alert.level)}
                    </span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p className="text-sm font-medium text-gray-900">
                        {alert.title}
                      </p>
                      <p className="text-sm text-gray-500" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {alert.message}
                      </p>
                      <p style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.25rem' }}>
                        {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {alerts?.length > 5 && (
              <div style={{ marginTop: '1rem' }}>
                <Link
                  to="/alerts"
                  className="text-sm text-blue-600"
                  style={{ color: '#2563eb' }}
                >
                  View all alerts →
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-body">
          <h3 className="text-lg font-medium text-gray-900" style={{ marginBottom: '1rem' }}>
            Quick Actions
          </h3>
          <div className="grid grid-cols-3" style={{ gap: '1rem' }}>
            <Link
              to="/analysis"
              className="btn btn-secondary"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textDecoration: 'none',
                padding: '0.75rem 1rem'
              }}
            >
              <ChartBarIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
              Run Analysis
            </Link>
            <Link
              to="/news"
              className="btn btn-secondary"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textDecoration: 'none',
                padding: '0.75rem 1rem'
              }}
            >
              <NewspaperIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
              View News
            </Link>
            <Link
              to="/settings"
              className="btn btn-secondary"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textDecoration: 'none',
                padding: '0.75rem 1rem'
              }}
            >
              <BuildingOfficeIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
              Manage Companies
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Company Card Component
const CompanyCard = ({ company, onClick, isSelected }) => {
  const { data: stats } = useQuery({
    queryKey: ['companyStats', company.name],
    queryFn: () => apiService.getCompanyStats(company.name),
    select: (response) => response.data
  });

  return (
    <div
      className={`company-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="flex justify-between items-center">
        <div style={{ flex: 1 }}>
          <div className="flex items-center" style={{ gap: '0.75rem' }}>
            <h4 className="text-lg font-medium text-gray-900">
              {company.name}
            </h4>
            {stats?.latest_contradiction_level && (
              <ContradictionBadge level={stats.latest_contradiction_level} />
            )}
          </div>
          <p className="text-sm text-gray-500" style={{ marginTop: '0.25rem' }}>
            {company.description || 'No description available'}
          </p>
          {company.industry && (
            <span className="badge badge-gray" style={{ marginTop: '0.5rem' }}>
              {company.industry}
            </span>
          )}
        </div>
        <div className="flex items-center" style={{ gap: '1rem' }}>
          <div style={{ textAlign: 'right' }}>
            <p className="text-sm font-medium text-gray-900">
              {stats?.document_count || 0} docs
            </p>
            <p className="text-sm text-gray-500">
              {stats?.news_count || 0} news
            </p>
          </div>
          <Link
            to={`/company/${company.name}`}
            style={{ padding: '0.5rem', color: '#9ca3af' }}
            onClick={(e) => e.stopPropagation()}
          >
            <EyeIcon style={{ height: '1.25rem', width: '1.25rem' }} />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;