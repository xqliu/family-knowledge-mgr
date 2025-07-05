import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BottomChat } from '../BottomChat';

// Mock fetch
global.fetch = vi.fn();

describe('BottomChat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock getCsrfToken
    document.body.innerHTML = '<input name="csrfmiddlewaretoken" value="test-token" />';
  });

  it('renders floating button initially', () => {
    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    expect(floatingBtn).toBeInTheDocument();
    expect(floatingBtn).toHaveClass('chat-floating-btn');
  });

  it('expands chat interface when floating button is clicked', () => {
    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    
    fireEvent.click(floatingBtn);
    
    expect(screen.getByText('💬 家庭知识助手')).toBeInTheDocument();
    expect(screen.getByText('询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('输入您的问题...')).toBeInTheDocument();
  });

  it('shows quick prompt buttons when expanded', () => {
    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    
    fireEvent.click(floatingBtn);
    
    expect(screen.getByText('爷爷的故事')).toBeInTheDocument();
    expect(screen.getByText('家族传统')).toBeInTheDocument();
    expect(screen.getByText('健康记录')).toBeInTheDocument();
  });

  it('collapses chat when close button is clicked', () => {
    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    
    fireEvent.click(floatingBtn);
    expect(screen.getByText('💬 家庭知识助手')).toBeInTheDocument();
    
    const closeBtn = screen.getByTitle('关闭');
    fireEvent.click(closeBtn);
    
    expect(screen.queryByText('💬 家庭知识助手')).not.toBeInTheDocument();
    expect(screen.getByTitle('打开家庭知识助手')).toBeInTheDocument();
  });

  it('sends message when quick prompt is clicked', async () => {
    const mockResponse = {
      response: 'AI response about 爷爷的故事',
      metadata: { query_type: 'general', confidence: 0.9 },
      sources: []
    };
    
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    fireEvent.click(floatingBtn);
    
    const quickPrompt = screen.getByText('爷爷的故事');
    fireEvent.click(quickPrompt);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/ai/chat/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test-token'
          },
          body: expect.stringContaining('爷爷的故事')
        })
      );
    });
  });

  it('sends message when user types and submits', async () => {
    const user = userEvent.setup();
    const mockResponse = {
      response: 'AI response',
      metadata: { query_type: 'general', confidence: 0.9 },
      sources: []
    };
    
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    fireEvent.click(floatingBtn);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    await user.type(input, 'Test message');
    await user.keyboard('{Enter}');
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/ai/chat/',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Test message')
        })
      );
    });
  });

  it('shows error message when API call fails', async () => {
    vi.mocked(global.fetch).mockRejectedValueOnce(new Error('Network error'));

    render(<BottomChat />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    fireEvent.click(floatingBtn);
    
    const quickPrompt = screen.getByText('爷爷的故事');
    fireEvent.click(quickPrompt);
    
    await waitFor(() => {
      expect(screen.getByText('抱歉，处理您的问题时出现了问题。请稍后再试。')).toBeInTheDocument();
    });
  });

  it('calls onSessionUpdate callback when provided', async () => {
    const onSessionUpdate = vi.fn();
    const mockResponse = {
      response: 'AI response',
      metadata: { query_type: 'general', confidence: 0.9 },
      sources: []
    };
    
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<BottomChat onSessionUpdate={onSessionUpdate} />);
    const floatingBtn = screen.getByTitle('打开家庭知识助手');
    fireEvent.click(floatingBtn);
    
    const quickPrompt = screen.getByText('爷爷的故事');
    fireEvent.click(quickPrompt);
    
    await waitFor(() => {
      expect(onSessionUpdate).toHaveBeenCalledWith(
        expect.objectContaining({
          id: expect.stringContaining('session-'),
          messages: expect.arrayContaining([
            expect.objectContaining({ content: '爷爷的故事', sender: 'user' }),
            expect.objectContaining({ content: 'AI response', sender: 'ai' })
          ])
        })
      );
    });
  });
});