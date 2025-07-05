import React, { useState, useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import type { ChatSession } from './types';
import './BottomChat.css';

interface BottomChatProps {
  onSessionUpdate?: (session: ChatSession) => void;
}

export const BottomChat: React.FC<BottomChatProps> = ({ onSessionUpdate }) => {
  const [messages, setMessages] = useState<ChatSession['messages']>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isExpanded, setIsExpanded] = useState(false);
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

  const getCsrfToken = (): string => {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.getAttribute('value');
    return token || '';
  };

  const toggleChat = () => {
    setIsExpanded(!isExpanded);
  };

  const quickPrompts = [
    "爷爷的故事",
    "家族传统",
    "健康记录"
  ];

  const handleQuickPrompt = (prompt: string) => {
    handleSendMessage(prompt);
  };

  return (
    <div className="bottom-chat">
      {/* Collapsed state - floating button */}
      {!isExpanded && (
        <button 
          className="chat-floating-btn"
          onClick={toggleChat}
          title="打开家庭知识助手"
        >
          💬
        </button>
      )}
      
      {/* Expanded state - chat interface */}
      {isExpanded && (
        <div className="chat-container">
          <div className="chat-header">
            <h3>💬 家庭知识助手</h3>
            <button 
              className="chat-close-btn"
              onClick={toggleChat}
              title="关闭"
            >
              ✕
            </button>
          </div>
          
          <div className="chat-body">
            {/* Welcome message */}
            {messages.length === 0 && (
              <div className="chat-welcome">
                <div className="welcome-icon">🤖</div>
                <p className="welcome-text">
                  询问家庭知识，比如：爷爷的创业故事、妈妈的生日安排...
                </p>
                
                {/* Quick prompts */}
                <div className="quick-prompts">
                  {quickPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      className="quick-prompt-btn"
                      onClick={() => handleQuickPrompt(prompt)}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Messages area */}
            <div className="chat-messages" ref={chatContainerRef}>
              {messages.length > 0 && (
                <MessageList messages={messages} isLoading={isLoading} />
              )}
            </div>
          </div>
          
          {/* Input area */}
          <div className="chat-input-area">
            <MessageInput 
              onSendMessage={handleSendMessage}
              disabled={isLoading}
              placeholder="输入您的问题..."
            />
          </div>
        </div>
      )}
    </div>
  );
};