import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../../../test-utils';
import { MessageInput } from '../MessageInput';

describe('MessageInput', () => {
  const mockOnSendMessage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with default props', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAttribute('maxLength', '1000');
    expect(textarea).toHaveAttribute('rows', '1');
    
    const sendButton = screen.getByTitle('发送消息 (Enter)');
    expect(sendButton).toBeInTheDocument();
    expect(sendButton).toBeDisabled(); // Should be disabled when no text
    
    expect(screen.getByText('0 / 1000')).toBeInTheDocument();
    expect(screen.getByText('按 Enter 发送，Shift+Enter 换行')).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} placeholder="自定义占位符" />);
    
    expect(screen.getByPlaceholderText('自定义占位符')).toBeInTheDocument();
  });

  it('renders in disabled state', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} disabled={true} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByTitle('发送消息 (Enter)');
    
    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
    expect(screen.getByText('⏳')).toBeInTheDocument(); // Loading icon when disabled
  });

  it('updates message state and character count when typing', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    
    fireEvent.change(textarea, { target: { value: 'Hello world' } });
    
    expect(textarea).toHaveValue('Hello world');
    expect(screen.getByText('11 / 1000')).toBeInTheDocument();
  });

  it('enables send button when message has content', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByTitle('发送消息 (Enter)');
    
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    
    expect(sendButton).not.toBeDisabled();
    expect(screen.getByText('➤')).toBeInTheDocument(); // Send icon
  });

  it('calls onSendMessage when form is submitted', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByTitle('发送消息 (Enter)');
    
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    expect(textarea).toHaveValue(''); // Should clear after sending
  });

  it('trims whitespace when sending message', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    
    fireEvent.change(textarea, { target: { value: '  Test message  ' } });
    fireEvent.submit(textarea.closest('form')!);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  it('does not send empty or whitespace-only messages', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    
    // Try to send empty message
    fireEvent.submit(textarea.closest('form')!);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
    
    // Try to send whitespace-only message
    fireEvent.change(textarea, { target: { value: '   ' } });
    fireEvent.submit(textarea.closest('form')!);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('does not send message when disabled', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} disabled={true} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.submit(textarea.closest('form')!);
    
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  describe('handleKeyDown functionality', () => {
    it('sends message on Enter key press', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
      expect(textarea).toHaveValue(''); // Should clear after sending
    });

    it('does not send message on Shift+Enter', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter', shiftKey: true });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      expect(textarea).toHaveValue('Test message'); // Should keep the message
    });

    it('does not send message on Enter when composing (IME input)', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: '测试消息' } });
      
      // Start composition (like typing Chinese/Japanese)
      fireEvent.compositionStart(textarea);
      
      // Press Enter while composing
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      expect(textarea).toHaveValue('测试消息'); // Should keep the message
    });

    it('allows Enter to send after composition ends', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: '测试消息' } });
      
      // Start and end composition
      fireEvent.compositionStart(textarea);
      fireEvent.compositionEnd(textarea);
      
      // Press Enter after composition ends
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('测试消息');
      expect(textarea).toHaveValue(''); // Should clear after sending
    });

    it('does not interfere with other key presses', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      // Press various keys that should not trigger send
      fireEvent.keyDown(textarea, { key: 'Escape', code: 'Escape' });
      fireEvent.keyDown(textarea, { key: 'Tab', code: 'Tab' });
      fireEvent.keyDown(textarea, { key: 'ArrowUp', code: 'ArrowUp' });
      fireEvent.keyDown(textarea, { key: 'Space', code: 'Space' });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      expect(textarea).toHaveValue('Test');
    });

    it('does not send empty message on Enter', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      // Press Enter without typing anything
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
    });

    it('does not send message on Enter when disabled', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} disabled={true} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      expect(textarea).toHaveValue('Test message');
    });
  });

  describe('handleCompositionStart and handleCompositionEnd functionality', () => {
    it('sets composing state on composition start', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: '你好' } });
      
      // Start composition
      fireEvent.compositionStart(textarea);
      
      // Try to send with Enter while composing
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
    });

    it('clears composing state on composition end', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      fireEvent.change(textarea, { target: { value: '你好世界' } });
      
      // Start composition, then end it
      fireEvent.compositionStart(textarea);
      fireEvent.compositionEnd(textarea);
      
      // Now Enter should work
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('你好世界');
    });

    it('handles multiple composition cycles correctly', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      // First composition cycle
      fireEvent.compositionStart(textarea);
      fireEvent.change(textarea, { target: { value: '你好' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      
      fireEvent.compositionEnd(textarea);
      
      // Second composition cycle
      fireEvent.compositionStart(textarea);
      fireEvent.change(textarea, { target: { value: '你好世界' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      
      fireEvent.compositionEnd(textarea);
      
      // Now Enter should work
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      expect(mockOnSendMessage).toHaveBeenCalledWith('你好世界');
    });

    it('composition events do not interfere with normal typing', () => {
      render(<MessageInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('输入您的问题...');
      
      // Normal typing should work fine
      fireEvent.change(textarea, { target: { value: 'Hello' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('Hello');
      
      // Reset mock
      mockOnSendMessage.mockClear();
      
      // Composition then normal typing
      fireEvent.compositionStart(textarea);
      fireEvent.change(textarea, { target: { value: '你好' } });
      fireEvent.compositionEnd(textarea);
      
      fireEvent.change(textarea, { target: { value: '你好 World' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('你好 World');
    });
  });

  it('auto-resizes textarea based on content', async () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...') as HTMLTextAreaElement;
    
    // Mock scrollHeight to simulate content height
    Object.defineProperty(textarea, 'scrollHeight', {
      configurable: true,
      value: 100
    });
    
    fireEvent.change(textarea, { target: { value: 'Line 1\nLine 2\nLine 3' } });
    
    await waitFor(() => {
      expect(textarea.style.height).toBe('100px');
    });
  });

  it('respects maxLength attribute', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('输入您的问题...');
    
    // Try to type more than 1000 characters
    const longMessage = 'a'.repeat(1001);
    fireEvent.change(textarea, { target: { value: longMessage } });
    
    // The textarea should enforce maxLength through HTML attribute
    expect(textarea).toHaveAttribute('maxLength', '1000');
  });
});