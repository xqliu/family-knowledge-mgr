import React, { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "输入您的问题..." 
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Enter (but not Shift+Enter)
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  return (
    <div className="message-input-container">
      <form onSubmit={handleSubmit} className="message-input-form">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onCompositionStart={handleCompositionStart}
            onCompositionEnd={handleCompositionEnd}
            placeholder={placeholder}
            disabled={disabled}
            className="message-textarea"
            rows={1}
            maxLength={1000}
          />
          
          <button
            type="submit"
            disabled={disabled || !message.trim()}
            className="send-button"
            title="发送消息 (Enter)"
          >
            {disabled ? (
              <span className="send-icon loading">⏳</span>
            ) : (
              <span className="send-icon">➤</span>
            )}
          </button>
        </div>
        
        <div className="input-footer">
          <span className="char-count">
            {message.length} / 1000
          </span>
          <span className="input-hint">
            按 Enter 发送，Shift+Enter 换行
          </span>
        </div>
      </form>
    </div>
  );
};