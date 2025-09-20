import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import {
  CogIcon,
  PlusIcon,
  DocumentArrowUpIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const Settings = () => {
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [showUploadDoc, setShowUploadDoc] = useState(false);
  const queryClient = useQueryClient();

  // Fetch companies
  const { data: companies, isLoading: companiesLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: () => apiService.getCompanies(),
    select: (response) => response.data
  });

  return (
    <div style={{ maxWidth: '64rem', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center">
            <CogIcon style={{ height: '2rem', width: '2rem', color: '#6b7280', marginRight: '0.75rem' }} />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                System Settings
              </h1>
              <p className="text-sm text-gray-500">
                Manage companies, upload documents, and configure monitoring
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-body">
          <h2 className="text-lg font-medium text-gray-900" style={{ marginBottom: '1rem' }}>
            Quick Actions
          </h2>
          <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
            <button
              onClick={() => setShowAddCompany(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '1rem',
                border: '2px dashed #d1d5db',
                borderRadius: '0.5rem',
                backgroundColor: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = '#9ca3af';
                e.target.style.backgroundColor = '#f9fafb';
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = '#d1d5db';
                e.target.style.backgroundColor = 'white';
              }}
            >
              <PlusIcon style={{ height: '2rem', width: '2rem', color: '#9ca3af', marginRight: '0.75rem' }} />
              <div style={{ textAlign: 'left' }}>
                <div className="text-sm font-medium text-gray-900">
                  Add Company
                </div>
                <div className="text-sm text-gray-500">
                  Add a new company to monitor
                </div>
              </div>
            </button>

            <button
              onClick={() => setShowUploadDoc(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '1rem',
                border: '2px dashed #d1d5db',
                borderRadius: '0.5rem',
                backgroundColor: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = '#9ca3af';
                e.target.style.backgroundColor = '#f9fafb';
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = '#d1d5db';
                e.target.style.backgroundColor = 'white';
              }}
            >
              <DocumentArrowUpIcon style={{ height: '2rem', width: '2rem', color: '#9ca3af', marginRight: '0.75rem' }} />
              <div style={{ textAlign: 'left' }}>
                <div className="text-sm font-medium text-gray-900">
                  Upload Document
                </div>
                <div className="text-sm text-gray-500">
                  Upload company documents
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Companies Management */}
      <div className="card">
        <div className="card-body">
          <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
            <h2 className="text-lg font-medium text-gray-900">
              Monitored Companies
            </h2>
            <span className="text-sm text-gray-500">
              {companies?.length || 0} companies
            </span>
          </div>

          {companiesLoading ? (
            <div className="flex justify-center items-center" style={{ height: '8rem' }}>
              <LoadingSpinner />
            </div>
          ) : companies?.length === 0 ? (
            <div className="text-center" style={{ padding: '3rem' }}>
              <BuildingOfficeIcon style={{ margin: '0 auto', height: '3rem', width: '3rem', color: '#9ca3af' }} />
              <h3 style={{ marginTop: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>No companies</h3>
              <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#6b7280' }}>
                Get started by adding your first company to monitor.
              </p>
              <div style={{ marginTop: '1.5rem' }}>
                <button
                  onClick={() => setShowAddCompany(true)}
                  className="btn btn-primary"
                >
                  <PlusIcon style={{ height: '1.25rem', width: '1.25rem', marginRight: '0.5rem' }} />
                  Add Company
                </button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {companies.map((company) => (
                <CompanyItem key={company.name} company={company} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <div className="card-body">
          <h2 className="text-lg font-medium text-gray-900" style={{ marginBottom: '1rem' }}>
            System Status
          </h2>
          <SystemStatus />
        </div>
      </div>

      {/* Modals */}
      {showAddCompany && (
        <AddCompanyModal
          onClose={() => setShowAddCompany(false)}
          onSuccess={() => {
            queryClient.invalidateQueries(['companies']);
            setShowAddCompany(false);
          }}
        />
      )}

      {showUploadDoc && (
        <UploadDocumentModal
          companies={companies}
          onClose={() => setShowUploadDoc(false)}
          onSuccess={() => {
            setShowUploadDoc(false);
          }}
        />
      )}
    </div>
  );
};

// Company Item Component
const CompanyItem = ({ company }) => {
  const { data: stats } = useQuery({
    queryKey: ['companyStats', company.name],
    queryFn: () => apiService.getCompanyStats(company.name),
    select: (response) => response.data
  });

  return (
    <div className="flex justify-between items-center" style={{
      padding: '1rem',
      border: '1px solid #e5e7eb',
      borderRadius: '0.5rem'
    }}>
      <div style={{ flex: 1 }}>
        <div className="flex items-center" style={{ gap: '0.75rem' }}>
          <BuildingOfficeIcon style={{ height: '1.5rem', width: '1.5rem', color: '#9ca3af' }} />
          <div>
            <h3 className="text-sm font-medium text-gray-900">
              {company.name}
            </h3>
            <p className="text-sm text-gray-500">
              {company.description || 'No description'}
            </p>
            {company.industry && (
              <span className="badge badge-gray" style={{ marginTop: '0.25rem' }}>
                {company.industry}
              </span>
            )}
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
        <div>{stats?.document_count || 0} documents</div>
        <div>{stats?.news_count || 0} news articles</div>
        <div>{stats?.analysis_count || 0} analyses</div>
      </div>
    </div>
  );
};

// System Status Component
const SystemStatus = () => {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiService.healthCheck(),
    select: (response) => response.data,
    refetchInterval: 30000,
  });

  const services = [
    {
      name: 'AI Service',
      status: health?.services?.ai_service ? 'operational' : 'degraded',
      description: 'Gemini AI for contradiction analysis'
    },
    {
      name: 'Vector Store',
      status: health?.services?.vector_store ? 'operational' : 'degraded',
      description: 'Document embeddings and search'
    },
    {
      name: 'Database',
      status: health?.services?.database ? 'operational' : 'degraded',
      description: 'Data storage and retrieval'
    }
  ];

  const getStatusClass = (status) => {
    switch (status) {
      case 'operational': return 'status-operational';
      case 'degraded': return 'status-degraded';
      case 'down': return 'status-down';
      default: return 'status-degraded';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {services.map((service) => (
        <div key={service.name} className="flex justify-between items-center" style={{
          padding: '0.75rem',
          backgroundColor: '#f9fafb',
          borderRadius: '0.5rem'
        }}>
          <div>
            <div className="text-sm font-medium text-gray-900">
              {service.name}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
              {service.description}
            </div>
          </div>
          <span className={`status-indicator ${getStatusClass(service.status)}`}>
            {service.status}
          </span>
        </div>
      ))}
    </div>
  );
};

// Add Company Modal
const AddCompanyModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    industry: '',
    website: ''
  });

  const mutation = useMutation({
    mutationFn: (data) => apiService.addCompany(data),
    onSuccess: () => {
      toast.success('Company added successfully!');
      onSuccess();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to add company');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name) {
      toast.error('Company name is required');
      return;
    }
    mutation.mutate(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="text-lg font-medium text-gray-900">
            Add New Company
          </h3>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">
                Company Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="form-input form-textarea"
                style={{ height: '5rem', resize: 'none' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Industry
              </label>
              <input
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({...formData, industry: e.target.value})}
                className="form-input"
                placeholder="e.g., Technology, Finance, Healthcare"
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Website
              </label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData({...formData, website: e.target.value})}
                className="form-input"
                placeholder="https://example.com"
              />
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
              'Add Company'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

// Upload Document Modal
const UploadDocumentModal = ({ companies, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    company: '',
    docType: '',
    file: null
  });

  const mutation = useMutation({
    mutationFn: ({ company, docType, file }) => apiService.uploadDocument(company, docType, file),
    onSuccess: () => {
      toast.success('Document uploaded successfully!');
      onSuccess();
    },
    onError: (error) => {
      const errorMessage = error.response?.data?.detail;
      if (Array.isArray(errorMessage)) {
        toast.error(errorMessage.map(err => err.msg || err).join(', '));
      } else {
        toast.error(errorMessage || 'Failed to upload document');
      }
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.company || !formData.docType || !formData.file) {
      toast.error('Please fill in all fields and select a file');
      return;
    }
    mutation.mutate(formData);
  };

  const docTypes = [
    'ESG Report',
    'Annual Report',
    'Code of Conduct',
    'Mission Statement',
    'Sustainability Report',
    'Diversity Report',
    'Other'
  ];

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="text-lg font-medium text-gray-900">
            Upload Company Document
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
                Document Type *
              </label>
              <select
                value={formData.docType}
                onChange={(e) => setFormData({...formData, docType: e.target.value})}
                className="form-input form-select"
                required
              >
                <option value="">Select type...</option>
                {docTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                File *
              </label>
              <input
                type="file"
                onChange={(e) => setFormData({...formData, file: e.target.files[0]})}
                className="form-input"
                accept=".pdf,.txt,.doc,.docx"
                required
              />
              <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#6b7280' }}>
                Supported formats: PDF, TXT, DOC, DOCX
              </p>
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
                Uploading...
              </>
            ) : (
              'Upload'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;