import React from 'react';
import type { Message } from './types';
import { MessageBubble } from './MessageBubble';
import { LoadingIndicator } from './LoadingIndicator';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ 
  messages, 
  isLoading = false 
}) => {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
        />
      ))}
      
      {isLoading && (
        <div className="message-bubble ai-message">
          <div className="message-header">
            <span className="sender-name">家庭智慧助手</span>
            <span className="message-time">正在思考...</span>
          </div>
          <div className="message-content">
            <LoadingIndicator />
          </div>
        </div>
      )}
    </div>
  );
};