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
});