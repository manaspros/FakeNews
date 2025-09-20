import React from 'react';

const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClass = size === 'sm' ? 'loading-spinner' : 'loading-spinner loading-spinner-lg';

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className={sizeClass} />
    </div>
  );
};

export default LoadingSpinner;