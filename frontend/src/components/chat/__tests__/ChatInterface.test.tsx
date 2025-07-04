import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../../../test-utils';
import { ChatInterface } from '../ChatInterface';

// Mock fetch with proper typing
const mockFetch = vi.fn() as vi.MockedFunction<typeof fetch>;
global.fetch = mockFetch;

describe('ChatInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders welcome screen initially', () => {
    render(<ChatInterface />);
    
    expect(screen.getByText('欢迎使用家庭智慧助手')).toBeInTheDocument();
    expect(screen.getByText('告诉我一些家庭传统故事')).toBeInTheDocument();
    expect(screen.getByText('我们家有哪些重要的庆祝活动？')).toBeInTheDocument();
    expect(screen.getByText('分享一些家族智慧')).toBeInTheDocument();
  });

  it('shows chat header with title and description', () => {
    render(<ChatInterface />);
    
    expect(screen.getByText('家庭智慧助手')).toBeInTheDocument();
    expect(screen.getByText('询问关于家庭记忆、传统和智慧的问题')).toBeInTheDocument();
  });

  it('has a message input with placeholder', () => {
    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText('询问关于家庭的问题...');
    expect(input).toBeInTheDocument();
  });

  it('has a clear chat button that is initially disabled', () => {
    render(<ChatInterface />);
    
    const clearButton = screen.getByText('清空对话');
    expect(clearButton).toBeInTheDocument();
    expect(clearButton).toBeDisabled();
  });

  it('can send a message through example query button', async () => {
    const mockResponse = {
      query: '告诉我一些家庭传统故事',
      response: '根据您的家庭记录，我找到了一些传统故事...',
      sources: [],
      metadata: {
        query_type: 'memory_discovery',
        confidence: 0.8,
        processing_time: 1.5,
        sources_count: 0,
        language: 'zh-CN'
      }
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    } as Response);

    render(<ChatInterface />);
    
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    // Should show loading indicator
    await waitFor(() => {
      expect(screen.getByText('正在思考...')).toBeInTheDocument();
    });

    // Should show the response
    await waitFor(() => {
      expect(screen.getByText('根据您的家庭记录，我找到了一些传统故事...')).toBeInTheDocument();
    });

    // Should show metadata
    expect(screen.getByText('记忆发现')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<ChatInterface />);
    
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    await waitFor(() => {
      expect(screen.getByText('抱歉，处理您的问题时出现了问题。请稍后再试。')).toBeInTheDocument();
    });
  });

  it('can clear chat messages', async () => {
    const mockResponse = {
      query: 'test',
      response: 'test response',
      sources: [],
      metadata: {
        query_type: 'general',
        confidence: 0.8,
        processing_time: 1.0,
        sources_count: 0,
        language: 'en-US'
      }
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    } as Response);

    render(<ChatInterface />);
    
    // Send a message first
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    await waitFor(() => {
      expect(screen.getByText('test response')).toBeInTheDocument();
    });

    // Clear chat
    const clearButton = screen.getByText('清空对话');
    expect(clearButton).not.toBeDisabled();
    fireEvent.click(clearButton);

    // Should return to welcome screen
    expect(screen.getByText('欢迎使用家庭智慧助手')).toBeInTheDocument();
    expect(clearButton).toBeDisabled();
  });

  it('sends manual input messages', async () => {
    const mockResponse = {
      query: '自定义问题',
      response: '这是回答',
      sources: [],
      metadata: {
        query_type: 'general',
        confidence: 0.7,
        processing_time: 0.8,
        sources_count: 0,
        language: 'zh-CN'
      }
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    } as Response);

    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText('询问关于家庭的问题...');
    const sendButton = screen.getByTitle('发送消息 (Enter)');

    fireEvent.change(input, { target: { value: '自定义问题' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('这是回答')).toBeInTheDocument();
    });
  });

  it('handles HTTP error responses (!response.ok)', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({})
    } as Response);

    render(<ChatInterface />);
    
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    await waitFor(() => {
      expect(screen.getByText('抱歉，处理您的问题时出现了问题。请稍后再试。')).toBeInTheDocument();
    });
  });

  it('handles API error responses (data.error)', async () => {
    const errorResponse = {
      error: 'API服务暂时不可用'
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(errorResponse)
    } as Response);

    render(<ChatInterface />);
    
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    await waitFor(() => {
      expect(screen.getByText('抱歉，处理您的问题时出现了问题。请稍后再试。')).toBeInTheDocument();
    });
  });

  it('calls onSessionUpdate callback when provided', async () => {
    const mockResponse = {
      query: '测试问题',
      response: '测试回答',
      sources: [],
      metadata: {
        query_type: 'general',
        confidence: 0.8,
        processing_time: 1.0,
        sources_count: 0,
        language: 'zh-CN'
      }
    };

    const mockOnSessionUpdate = vi.fn();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    } as Response);

    render(<ChatInterface onSessionUpdate={mockOnSessionUpdate} />);
    
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    await waitFor(() => {
      expect(screen.getByText('测试回答')).toBeInTheDocument();
    });

    // Verify onSessionUpdate was called
    expect(mockOnSessionUpdate).toHaveBeenCalledTimes(1);
    
    const sessionUpdate = mockOnSessionUpdate.mock.calls[0][0];
    expect(sessionUpdate).toHaveProperty('id');
    expect(sessionUpdate).toHaveProperty('messages');
    expect(sessionUpdate).toHaveProperty('createdAt');
    expect(sessionUpdate).toHaveProperty('updatedAt');
    expect(sessionUpdate.messages).toHaveLength(2); // User message + AI response
    expect(sessionUpdate.messages[0].sender).toBe('user');
    expect(sessionUpdate.messages[1].sender).toBe('ai');
  });

  it('does not call onSessionUpdate when callback is not provided', async () => {
    const mockResponse = {
      query: '测试问题',
      response: '测试回答',
      sources: [],
      metadata: {
        query_type: 'general',
        confidence: 0.8,
        processing_time: 1.0,
        sources_count: 0,
        language: 'zh-CN'
      }
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    } as Response);

    // Render without onSessionUpdate callback
    render(<ChatInterface />);
    
    const exampleButton = screen.getByText('告诉我一些家庭传统故事');
    fireEvent.click(exampleButton);

    await waitFor(() => {
      expect(screen.getByText('测试回答')).toBeInTheDocument();
    });

    // Should not crash and should complete normally
    expect(screen.getByText('测试回答')).toBeInTheDocument();
  });

  // Tests for bottom chat modal functionality
  describe('Bottom Chat Modal', () => {
    it('renders bottom chat input with correct placeholder', () => {
      render(<ChatInterface className="bottom-chat" />);
      
      const input = screen.getByPlaceholderText('🤖 询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排...');
      expect(input).toBeInTheDocument();
    });

    it('shows chat modal overlay when messages exist in bottom chat', async () => {
      const mockResponse = {
        query: '测试问题',
        response: '测试回答',
        sources: [],
        metadata: {
          query_type: 'general',
          confidence: 0.8,
          processing_time: 1.0,
          sources_count: 0,
          language: 'zh-CN'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      } as Response);

      render(<ChatInterface className="bottom-chat" />);
      
      // Send a message to trigger the modal
      const input = screen.getByPlaceholderText('🤖 询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排...');
      const sendButton = screen.getByTitle('发送消息 (Enter)');

      fireEvent.change(input, { target: { value: '测试问题' } });
      fireEvent.click(sendButton);

      // Wait for response and modal to appear
      await waitFor(() => {
        expect(screen.getByText('🤖 AI助手对话')).toBeInTheDocument();
        expect(screen.getByText('测试回答')).toBeInTheDocument();
      });

      // Check modal elements exist
      expect(screen.getByText('🤖 AI助手对话')).toBeInTheDocument();
      expect(screen.getByText('×')).toBeInTheDocument(); // Close button
      expect(screen.getByPlaceholderText('继续对话...')).toBeInTheDocument();
    });

    it('closes modal when close button is clicked', async () => {
      const mockResponse = {
        query: '测试问题',
        response: '测试回答',
        sources: [],
        metadata: {
          query_type: 'general',
          confidence: 0.8,
          processing_time: 1.0,
          sources_count: 0,
          language: 'zh-CN'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      } as Response);

      render(<ChatInterface className="bottom-chat" />);
      
      // Send a message to trigger the modal
      const input = screen.getByPlaceholderText('🤖 询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排...');
      const sendButton = screen.getByTitle('发送消息 (Enter)');

      fireEvent.change(input, { target: { value: '测试问题' } });
      fireEvent.click(sendButton);

      // Wait for modal to appear
      await waitFor(() => {
        expect(screen.getByText('🤖 AI助手对话')).toBeInTheDocument();
      });

      // Close the modal
      const closeButton = screen.getByText('×');
      fireEvent.click(closeButton);

      // Modal should be gone
      expect(screen.queryByText('🤖 AI助手对话')).not.toBeInTheDocument();
      expect(screen.queryByText('测试回答')).not.toBeInTheDocument();
    });

    it('can send messages from within the modal', async () => {
      const mockResponse1 = {
        query: '第一个问题',
        response: '第一个回答',
        sources: [],
        metadata: { query_type: 'general', confidence: 0.8, processing_time: 1.0, sources_count: 0, language: 'zh-CN' }
      };

      const mockResponse2 = {
        query: '第二个问题',
        response: '第二个回答',
        sources: [],
        metadata: { query_type: 'general', confidence: 0.8, processing_time: 1.0, sources_count: 0, language: 'zh-CN' }
      };

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockResponse1)
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockResponse2)
        } as Response);

      render(<ChatInterface className="bottom-chat" />);
      
      // Send first message
      const input = screen.getByPlaceholderText('🤖 询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排...');
      const sendButton = screen.getByTitle('发送消息 (Enter)');

      fireEvent.change(input, { target: { value: '第一个问题' } });
      fireEvent.click(sendButton);

      // Wait for modal to appear
      await waitFor(() => {
        expect(screen.getByText('第一个回答')).toBeInTheDocument();
      });

      // Send second message from modal
      const modalInput = screen.getByPlaceholderText('继续对话...');
      const modalSendButton = screen.getAllByTitle('发送消息 (Enter)')[1]; // Second send button in modal

      fireEvent.change(modalInput, { target: { value: '第二个问题' } });
      fireEvent.click(modalSendButton);

      // Wait for second response
      await waitFor(() => {
        expect(screen.getByText('第二个回答')).toBeInTheDocument();
      });

      // Both messages should be visible
      expect(screen.getByText('第一个回答')).toBeInTheDocument();
      expect(screen.getByText('第二个回答')).toBeInTheDocument();
    });

    it('does not show modal for regular chat interface', async () => {
      const mockResponse = {
        query: '测试问题',
        response: '测试回答',
        sources: [],
        metadata: {
          query_type: 'general',
          confidence: 0.8,
          processing_time: 1.0,
          sources_count: 0,
          language: 'zh-CN'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      } as Response);

      // Render regular chat interface (without bottom-chat class)
      render(<ChatInterface />);
      
      const exampleButton = screen.getByText('告诉我一些家庭传统故事');
      fireEvent.click(exampleButton);

      await waitFor(() => {
        expect(screen.getByText('测试回答')).toBeInTheDocument();
      });

      // Should not show modal elements
      expect(screen.queryByText('🤖 AI助手对话')).not.toBeInTheDocument();
      expect(screen.queryByText('×')).not.toBeInTheDocument();
    });
  });
});