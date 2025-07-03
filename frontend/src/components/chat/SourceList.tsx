import React from 'react';
import type { ChatSource } from './types';

interface SourceListProps {
  sources: ChatSource[];
}

export const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  const getSourceIcon = (type: string): string => {
    const icons: { [key: string]: string } = {
      'story': '📖',
      'event': '🎉',
      'heritage': '🏛️',
      'health': '🏥',
      'person': '👤',
      'multimedia': '🎬',
      'default': '📄'
    };
    return icons[type] || icons.default;
  };

  const getSourceTypeLabel = (type: string): string => {
    const labels: { [key: string]: string } = {
      'story': '家庭故事',
      'event': '重要事件',
      'heritage': '文化传承',
      'health': '健康记录',
      'person': '家庭成员',
      'multimedia': '多媒体',
      'default': '其他'
    };
    return labels[type] || labels.default;
  };

  const getRelevanceColor = (relevance: number): string => {
    if (relevance >= 0.8) return '#10b981'; // Green
    if (relevance >= 0.6) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  return (
    <div className="source-list">
      {sources.map((source, index) => (
        <div key={`${source.type}-${source.id}-${index}`} className="source-item">
          <div className="source-header">
            <span className="source-icon">{getSourceIcon(source.type)}</span>
            <span className="source-type">{getSourceTypeLabel(source.type)}</span>
            <span 
              className="source-relevance"
              style={{ color: getRelevanceColor(source.relevance) }}
            >
              {(source.relevance * 100).toFixed(0)}%
            </span>
          </div>
          
          <div className="source-content">
            <h4 className="source-title">{source.title}</h4>
            
            {/* Source-specific details */}
            {source.story_type && (
              <span className="source-detail">
                <strong>故事类型:</strong> {source.story_type}
              </span>
            )}
            
            {source.event_type && (
              <span className="source-detail">
                <strong>事件类型:</strong> {source.event_type}
              </span>
            )}
            
            {source.heritage_type && (
              <span className="source-detail">
                <strong>传承类型:</strong> {source.heritage_type}
              </span>
            )}
            
            {source.person && (
              <span className="source-detail">
                <strong>相关人员:</strong> {source.person}
              </span>
            )}
            
            {source.people && source.people.length > 0 && (
              <span className="source-detail">
                <strong>涉及人员:</strong> {source.people.join(', ')}
              </span>
            )}
            
            {source.date && (
              <span className="source-detail">
                <strong>日期:</strong> {source.date}
              </span>
            )}
            
            {source.importance && (
              <span className="source-detail">
                <strong>重要程度:</strong> {source.importance}
              </span>
            )}
            
            {source.is_hereditary && (
              <span className="source-detail hereditary">
                <strong>遗传性:</strong> 是
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};