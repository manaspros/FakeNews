import React from 'react';

const ContradictionBadge = ({ level, confidence = null, size = 'md' }) => {
  const getIcon = (level) => {
    switch (level?.toUpperCase()) {
      case 'HIGH':
        return '🚨';
      case 'MEDIUM':
        return '⚠️';
      case 'LOW':
        return '🟡';
      case 'NONE':
        return '✅';
      default:
        return '❓';
    }
  };

  const getBadgeClass = (level) => {
    switch (level?.toUpperCase()) {
      case 'HIGH':
        return 'badge badge-high';
      case 'MEDIUM':
        return 'badge badge-medium';
      case 'LOW':
        return 'badge badge-low';
      case 'NONE':
        return 'badge badge-none';
      default:
        return 'badge badge-gray';
    }
  };

  const icon = getIcon(level);
  const badgeClass = getBadgeClass(level);

  return (
    <span className={badgeClass}>
      <span>{icon}</span>
      {level?.toUpperCase() || 'UNKNOWN'}
      {confidence && (
        <span style={{ opacity: 0.75, marginLeft: '0.25rem' }}>
          ({Math.round(confidence * 100)}%)
        </span>
      )}
    </span>
  );
};

export default ContradictionBadge;