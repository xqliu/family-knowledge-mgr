import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '../../../test-utils';
import { MessageBubble } from '../MessageBubble';
import type { Message } from '../types';

describe('MessageBubble', () => {
  const mockTimestamp = new Date('2023-12-25T10:30:00Z');

  const basicUserMessage: Message = {
    id: '1',
    content: 'Hello, this is a user message',
    timestamp: mockTimestamp,
    sender: 'user',
    type: 'text'
  };

  const basicAiMessage: Message = {
    id: '2',
    content: 'This is an AI response',
    timestamp: mockTimestamp,
    sender: 'ai',
    type: 'text'
  };

  const aiMessageWithSources: Message = {
    id: '3',
    content: 'AI response with sources',
    timestamp: mockTimestamp,
    sender: 'ai',
    type: 'text',
    metadata: {
      queryType: 'general',
      confidence: 0.7,
      processingTime: 1.8,
      sources: [
        {
          type: 'story',
          id: 1,
          title: '家庭传统故事',
          relevance: 0.9,
          story_type: '传统',
          people: ['张三', '李四']
        },
        {
          type: 'event',
          id: 2,
          title: '重要庆祝活动',
          relevance: 0.8,
          event_type: '庆祝'
        }
      ]
    }
  };

  const errorMessage: Message = {
    id: '4',
    content: 'An error occurred',
    timestamp: mockTimestamp,
    sender: 'ai',
    type: 'error'
  };

  it('renders basic user message correctly', () => {
    render(<MessageBubble message={basicUserMessage} />);
    
    expect(screen.getByText('您')).toBeInTheDocument();
    expect(screen.getByText('Hello, this is a user message')).toBeInTheDocument();
  });

  it('renders basic AI message correctly', () => {
    render(<MessageBubble message={basicAiMessage} />);
    
    expect(screen.getByText('家庭智慧助手')).toBeInTheDocument();
    expect(screen.getByText('This is an AI response')).toBeInTheDocument();
  });

  it('renders error message with error icon', () => {
    render(<MessageBubble message={errorMessage} />);
    
    expect(screen.getByText('⚠️')).toBeInTheDocument();
    expect(screen.getByText('An error occurred')).toBeInTheDocument();
  });

  describe('Sources section', () => {
    it('renders sources toggle button when sources are present', () => {
      render(<MessageBubble message={aiMessageWithSources} />);
      
      expect(screen.getByText('📚')).toBeInTheDocument();
      expect(screen.getByText('显示 资料来源 (2)')).toBeInTheDocument();
    });

    it('does not render sources section when sources are empty', () => {
      const messageWithEmptySources: Message = {
        ...aiMessageWithSources,
        metadata: {
          ...aiMessageWithSources.metadata!,
          sources: []
        }
      };

      render(<MessageBubble message={messageWithEmptySources} />);
      
      expect(screen.queryByText('📚')).not.toBeInTheDocument();
      expect(screen.queryByText(/资料来源/)).not.toBeInTheDocument();
    });

    it('does not render sources section when sources are undefined', () => {
      const messageWithoutSources: Message = {
        ...aiMessageWithSources,
        metadata: {
          queryType: 'general',
          confidence: 0.7
        }
      };

      render(<MessageBubble message={messageWithoutSources} />);
      
      expect(screen.queryByText('📚')).not.toBeInTheDocument();
      expect(screen.queryByText(/资料来源/)).not.toBeInTheDocument();
    });

    it('toggles sources display when toggle button is clicked', () => {
      render(<MessageBubble message={aiMessageWithSources} />);
      
      const toggleButton = screen.getByText('显示 资料来源 (2)');
      
      // Initially sources should be hidden
      expect(screen.queryByText('家庭传统故事')).not.toBeInTheDocument();
      expect(screen.queryByText('重要庆祝活动')).not.toBeInTheDocument();
      
      // Click to show sources
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('隐藏 资料来源 (2)')).toBeInTheDocument();
      expect(screen.getByText('家庭传统故事')).toBeInTheDocument();
      expect(screen.getByText('重要庆祝活动')).toBeInTheDocument();
      
      // Click to hide sources again
      fireEvent.click(screen.getByText('隐藏 资料来源 (2)'));
      
      expect(screen.getByText('显示 资料来源 (2)')).toBeInTheDocument();
      expect(screen.queryByText('家庭传统故事')).not.toBeInTheDocument();
      expect(screen.queryByText('重要庆祝活动')).not.toBeInTheDocument();
    });

    it('displays correct sources count in toggle button', () => {
      const messageWithManySources: Message = {
        ...aiMessageWithSources,
        metadata: {
          ...aiMessageWithSources.metadata!,
          sources: [
            { type: 'story', id: 1, title: '故事1', relevance: 0.9 },
            { type: 'event', id: 2, title: '事件1', relevance: 0.8 },
            { type: 'heritage', id: 3, title: '传承1', relevance: 0.7 }
          ]
        }
      };

      render(<MessageBubble message={messageWithManySources} />);
      
      expect(screen.getByText('显示 资料来源 (3)')).toBeInTheDocument();
    });

    it('renders SourceList component when sources are shown', () => {
      render(<MessageBubble message={aiMessageWithSources} />);
      
      const toggleButton = screen.getByText('显示 资料来源 (2)');
      fireEvent.click(toggleButton);
      
      // Check that SourceList is rendered with the correct sources
      expect(screen.getByText('家庭传统故事')).toBeInTheDocument();
      expect(screen.getByText('重要庆祝活动')).toBeInTheDocument();
      expect(screen.getByText('家庭故事')).toBeInTheDocument(); // Source type label
      expect(screen.getByText('重要事件')).toBeInTheDocument(); // Source type label
      expect(screen.getByText('90%')).toBeInTheDocument(); // Relevance percentage
      expect(screen.getByText('80%')).toBeInTheDocument(); // Relevance percentage
    });
  });

  describe('Helper functions and metadata', () => {
    it('renders AI message metadata correctly', () => {
      const aiMessageWithMetadata: Message = {
        id: '5',
        content: 'AI response with metadata',
        timestamp: mockTimestamp,
        sender: 'ai',
        type: 'text',
        metadata: {
          queryType: 'memory_discovery',
          confidence: 0.85,
          processingTime: 2.5
        }
      };

      render(<MessageBubble message={aiMessageWithMetadata} />);
      
      expect(screen.getByText('类型:')).toBeInTheDocument();
      expect(screen.getByText('记忆发现')).toBeInTheDocument();
      expect(screen.getByText('置信度:')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('处理时间:')).toBeInTheDocument();
      expect(screen.getByText('2.50s')).toBeInTheDocument();
    });

    it('applies correct confidence color styling', () => {
      const testCases = [
        { confidence: 0.9, expectedColor: '#10b981' }, // High confidence - green
        { confidence: 0.7, expectedColor: '#f59e0b' }, // Medium confidence - yellow
        { confidence: 0.5, expectedColor: '#ef4444' } // Low confidence - red
      ];

      testCases.forEach(({ confidence, expectedColor }) => {
        const message: Message = {
          id: 'test',
          content: 'Test message',
          timestamp: mockTimestamp,
          sender: 'ai',
          type: 'text',
          metadata: { confidence }
        };

        render(<MessageBubble message={message} />);
        const confidenceElement = screen.getByText(`${(confidence * 100).toFixed(0)}%`);
        expect(confidenceElement).toHaveStyle(`color: ${expectedColor}`);
      });
    });

    it('renders query type labels correctly', () => {
      const testCases = [
        { queryType: 'memory_discovery', expected: '记忆发现' },
        { queryType: 'health_pattern', expected: '健康模式' },
        { queryType: 'general', expected: '一般问题' }
      ];

      testCases.forEach(({ queryType, expected }) => {
        const message: Message = {
          id: 'test',
          content: 'Test message',
          timestamp: mockTimestamp,
          sender: 'ai',
          type: 'text',
          metadata: { queryType }
        };

        render(<MessageBubble message={message} />);
        expect(screen.getByText(expected)).toBeInTheDocument();
      });
    });

    it('does not render metadata for user messages', () => {
      render(<MessageBubble message={basicUserMessage} />);
      
      expect(screen.queryByText('类型:')).not.toBeInTheDocument();
      expect(screen.queryByText('置信度:')).not.toBeInTheDocument();
      expect(screen.queryByText('处理时间:')).not.toBeInTheDocument();
    });

    it('handles optional metadata fields gracefully', () => {
      const partialMetadataMessage: Message = {
        id: 'test',
        content: 'Test message',
        timestamp: mockTimestamp,
        sender: 'ai',
        type: 'text',
        metadata: {
          queryType: 'general'
        }
      };

      render(<MessageBubble message={partialMetadataMessage} />);
      
      expect(screen.getByText('类型:')).toBeInTheDocument();
      expect(screen.getByText('一般问题')).toBeInTheDocument();
      expect(screen.queryByText('置信度:')).not.toBeInTheDocument();
      expect(screen.queryByText('处理时间:')).not.toBeInTheDocument();
    });
  });
});