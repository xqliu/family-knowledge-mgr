import React, { useState } from 'react';
import type { Message } from './types';
import { SourceList } from './SourceList';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showSources, setShowSources] = useState(false);

  const formatTime = (timestamp: Date): string => {
    return timestamp.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getSenderName = (sender: string): string => {
    return sender === 'user' ? '您' : '家庭智慧助手';
  };

  const getMessageTypeClass = (type: string): string => {
    switch (type) {
      case 'error': return 'error-message';
      default: return '';
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return '#10b981'; // Green
    if (confidence >= 0.6) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const getQueryTypeLabel = (queryType: string): string => {
    const labels: { [key: string]: string } = {
      'memory_discovery': '记忆发现',
      'health_pattern': '健康模式',
      'event_planning': '事件规划',
      'cultural_heritage': '文化传承',
      'relationship_discovery': '关系发现',
      'general': '一般问题'
    };
    return labels[queryType] || queryType;
  };

  return (
    <div className={`message-bubble ${message.sender}-message ${getMessageTypeClass(message.type)}`}>
      <div className="message-header">
        <span className="sender-name">{getSenderName(message.sender)}</span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>
      
      <div className="message-content">
        {message.type === 'error' && (
          <div className="error-icon">⚠️</div>
        )}
        <p className="message-text">{message.content}</p>
      </div>

      {message.sender === 'ai' && message.metadata && (
        <div className="message-metadata">
          <div className="metadata-row">
            <span className="metadata-item">
              <strong>类型:</strong> {getQueryTypeLabel(message.metadata.queryType || 'general')}
            </span>
            
            {message.metadata.confidence !== undefined && (
              <span className="metadata-item">
                <strong>置信度:</strong> 
                <span 
                  className="confidence-score"
                  style={{ color: getConfidenceColor(message.metadata.confidence) }}
                >
                  {(message.metadata.confidence * 100).toFixed(0)}%
                </span>
              </span>
            )}
            
            {message.metadata.processingTime !== undefined && (
              <span className="metadata-item">
                <strong>处理时间:</strong> {message.metadata.processingTime.toFixed(2)}s
              </span>
            )}
          </div>

          {message.metadata.sources && message.metadata.sources.length > 0 && (
            <div className="sources-section">
              <button 
                className="sources-toggle"
                onClick={() => setShowSources(!showSources)}
              >
                <span className="sources-icon">📚</span>
                {showSources ? '隐藏' : '显示'} 资料来源 ({message.metadata.sources.length})
              </button>
              
              {showSources && (
                <SourceList sources={message.metadata.sources} />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};