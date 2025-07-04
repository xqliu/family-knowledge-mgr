import React, { useState, useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import type { ChatSession } from './types';
import './ChatInterface.css';
import './BottomChat.css';

interface ChatInterfaceProps {
  className?: string;
  onSessionUpdate?: (session: ChatSession) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  className = '', 
  onSessionUpdate 
}) => {
  const [messages, setMessages] = useState<ChatSession['messages']>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [showChatModal, setShowChatModal] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Generate session ID on mount
  useEffect(() => {
    const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage = {
      id: `msg-${Date.now()}`,
      content,
      timestamp: new Date(),
      sender: 'user' as const,
      type: 'text' as const
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/ai/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          query: content,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const aiMessage = {
        id: `msg-${Date.now()}-ai`,
        content: data.response,
        timestamp: new Date(),
        sender: 'ai' as const,
        type: 'text' as const,
        metadata: {
          queryType: data.metadata?.query_type,
          confidence: data.metadata?.confidence,
          sources: data.sources || [],
          processingTime: data.metadata?.processing_time
        }
      };

      setMessages(prev => [...prev, aiMessage]);

      // Update session if callback provided
      if (onSessionUpdate) {
        onSessionUpdate({
          id: sessionId,
          messages: [...messages, userMessage, aiMessage],
          createdAt: new Date(),
          updatedAt: new Date()
        });
      }

    } catch (err) {
      console.error('Chat error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      
      // Add error message to chat
      const errorMessage = {
        id: `msg-${Date.now()}-error`,
        content: '抱歉，处理您的问题时出现了问题。请稍后再试。',
        timestamp: new Date(),
        sender: 'ai' as const,
        type: 'error' as const
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  const getCsrfToken = (): string => {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.getAttribute('value');
    return token || '';
  };

  // Check if this is the bottom chat (simplified version)
  const isBottomChat = className.includes('bottom-chat');

  if (isBottomChat) {
    return (
      <div className={`chat-interface ${className}`}>
        <div className="bottom-chat-container">
          <MessageInput 
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder="🤖 询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排..."
          />
          
          {/* Chat history button */}
          <button 
            className="chat-history-btn"
            onClick={() => setShowChatModal(true)}
            title="查看对话历史"
          >
            💬
          </button>
        </div>
        
        {/* Show messages in modal/overlay when there are active conversations or when manually opened */}
        {(messages.length > 0 || showChatModal) && (
          <div className="chat-overlay">
            <div className="chat-modal">
              <div className="chat-modal-header">
                <h3>🤖 AI助手对话</h3>
                <button 
                  className="close-chat"
                  onClick={() => {
                    setMessages([]);
                    setShowChatModal(false);
                  }}
                >
                  ×
                </button>
              </div>
              
              <div className="chat-modal-container" ref={chatContainerRef}>
                {messages.length === 0 ? (
                  <div className="empty-chat-message">
                    <div className="empty-chat-icon">🤖</div>
                    <p>还没有对话记录</p>
                    <p className="empty-chat-hint">在下方输入框开始与AI助手对话吧！</p>
                  </div>
                ) : (
                  <MessageList messages={messages} isLoading={isLoading} />
                )}
              </div>
              
              <div className="chat-modal-input">
                <MessageInput 
                  onSendMessage={handleSendMessage}
                  disabled={isLoading}
                  placeholder="继续对话..."
                />
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Full chat interface for desktop sidebar or dedicated chat pages
  return (
    <div className={`chat-interface ${className}`}>
      <div className="chat-header">
        <h3>家庭智慧助手</h3>
        <p className="chat-subtitle">询问关于家庭记忆、传统和智慧的问题</p>
        <button 
          className="clear-chat-btn"
          onClick={handleClearChat}
          disabled={messages.length === 0}
        >
          清空对话
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
          <button 
            className="error-dismiss"
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      <div 
        className="chat-container"
        ref={chatContainerRef}
      >
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="welcome-icon">🏠</div>
            <h4>欢迎使用家庭智慧助手</h4>
            <p>您可以询问关于家庭故事、传统、健康记录、重要事件等问题。</p>
            <div className="example-queries">
              <h5>示例问题：</h5>
              <button 
                className="example-query"
                onClick={() => handleSendMessage('告诉我一些家庭传统故事')}
              >
                告诉我一些家庭传统故事
              </button>
              <button 
                className="example-query"
                onClick={() => handleSendMessage('我们家有哪些重要的庆祝活动？')}
              >
                我们家有哪些重要的庆祝活动？
              </button>
              <button 
                className="example-query"
                onClick={() => handleSendMessage('分享一些家族智慧')}
              >
                分享一些家族智慧
              </button>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} isLoading={isLoading} />
        )}
      </div>

      <MessageInput 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder="询问关于家庭的问题..."
      />
    </div>
  );
};