import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useWebSocket } from '../context/WebSocketContext';
import { ExclamationTriangleIcon, BellIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);
  const location = useLocation();
  const { isConnected, alerts, clearAlerts, removeAlert } = useWebSocket();

  const navigation = [
    { name: 'Dashboard', href: '/', current: location.pathname === '/' },
    { name: 'Analysis', href: '/analysis', current: location.pathname === '/analysis' },
    { name: 'News', href: '/news', current: location.pathname === '/news' },
    { name: 'Settings', href: '/settings', current: location.pathname === '/settings' },
  ];

  const unreadAlerts = alerts.filter(alert => !alert.read);

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="flex items-center">
          <Link to="/" className="navbar-brand">
            <ExclamationTriangleIcon style={{ width: '2rem', height: '2rem', marginRight: '0.5rem', color: '#dc2626' }} />
            <span>Hypocrisy Detector</span>
          </Link>

          <div className="navbar-nav" style={{ marginLeft: '3rem' }}>
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={item.current ? 'active' : ''}
                style={{
                  textDecoration: 'none',
                  color: item.current ? '#dc2626' : '#6b7280',
                  fontWeight: '500',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.375rem',
                  backgroundColor: item.current ? '#fef2f2' : 'transparent',
                  transition: 'all 0.2s'
                }}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>

        <div className="navbar-actions">
          {/* Connection Status */}
          <div className="connection-status">
            <div
              className={`status-dot ${isConnected ? 'status-connected' : 'status-disconnected'}`}
            />
            <span>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Alerts Bell */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowAlerts(!showAlerts)}
              className="btn btn-secondary btn-sm"
              style={{ position: 'relative' }}
            >
              <BellIcon style={{ width: '1.25rem', height: '1.25rem' }} />
              {unreadAlerts.length > 0 && (
                <span
                  style={{
                    position: 'absolute',
                    top: '-0.25rem',
                    right: '-0.25rem',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '0.125rem 0.5rem',
                    fontSize: '0.75rem',
                    fontWeight: 'bold',
                    color: 'white',
                    backgroundColor: '#dc2626',
                    borderRadius: '9999px',
                    minWidth: '1.25rem',
                    height: '1.25rem'
                  }}
                >
                  {unreadAlerts.length}
                </span>
              )}
            </button>

            {/* Alerts Dropdown */}
            {showAlerts && (
              <div
                style={{
                  position: 'absolute',
                  right: 0,
                  marginTop: '0.5rem',
                  width: '24rem',
                  backgroundColor: 'white',
                  borderRadius: '0.375rem',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb',
                  zIndex: 50
                }}
              >
                <div style={{ padding: '1rem', maxHeight: '24rem', overflowY: 'auto' }}>
                  <div className="flex justify-between items-center" style={{ marginBottom: '1rem', borderBottom: '1px solid #e5e7eb', paddingBottom: '0.5rem' }}>
                    <h3 className="text-lg font-medium">Alerts</h3>
                    {alerts.length > 0 && (
                      <button
                        onClick={clearAlerts}
                        className="text-sm text-gray-500"
                        style={{ color: '#6b7280', fontSize: '0.875rem' }}
                      >
                        Clear All
                      </button>
                    )}
                  </div>
                  {alerts.length === 0 ? (
                    <div style={{ padding: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                      No alerts
                    </div>
                  ) : (
                    alerts.slice(0, 10).map((alert) => (
                      <div
                        key={alert.id}
                        style={{
                          padding: '0.75rem',
                          borderBottom: '1px solid #f3f4f6',
                          cursor: 'pointer'
                        }}
                        onMouseEnter={(e) => e.target.style.backgroundColor = '#f9fafb'}
                        onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                      >
                        <div className="flex justify-between items-start">
                          <div style={{ flex: 1 }}>
                            <div className="flex items-center" style={{ marginBottom: '0.25rem' }}>
                              <span
                                className={`badge ${
                                  alert.level === 'HIGH'
                                    ? 'badge-high'
                                    : alert.level === 'MEDIUM'
                                    ? 'badge-medium'
                                    : 'badge-low'
                                }`}
                                style={{ marginRight: '0.5rem' }}
                              >
                                {alert.level}
                              </span>
                              <span className="font-medium text-sm">
                                {alert.company}
                              </span>
                            </div>
                            <p style={{ fontSize: '0.875rem', color: '#4b5563', marginBottom: '0.25rem' }}>
                              {alert.message}
                            </p>
                            <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                              {new Date(alert.timestamp).toLocaleString()}
                            </p>
                          </div>
                          <button
                            onClick={() => removeAlert(alert.id)}
                            style={{ marginLeft: '0.5rem', color: '#9ca3af', padding: '0.25rem' }}
                          >
                            <XMarkIcon style={{ width: '1rem', height: '1rem' }} />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="btn btn-secondary btn-sm"
            style={{ display: 'none' }}
          >
            {isOpen ? (
              <XMarkIcon style={{ width: '1.25rem', height: '1.25rem' }} />
            ) : (
              <Bars3Icon style={{ width: '1.25rem', height: '1.25rem' }} />
            )}
          </button>
        </div>
      </div>

      {/* Click outside to close alerts */}
      {showAlerts && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 40
          }}
          onClick={() => setShowAlerts(false)}
        />
      )}

      <style jsx>{`
        @media (max-width: 768px) {
          .navbar-nav {
            display: none !important;
          }
          .btn[style*="display: none"] {
            display: inline-flex !important;
          }
        }
      `}</style>
    </nav>
  );
};

export default Navbar;