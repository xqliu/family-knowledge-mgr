import React from 'react';

export const LoadingIndicator: React.FC = () => {
  return (
    <div className="loading-indicator">
      <div className="typing-animation">
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
      </div>
      <span className="loading-text">正在处理您的问题...</span>
    </div>
  );
};