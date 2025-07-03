export interface Message {
  id: string;
  content: string;
  timestamp: Date;
  sender: 'user' | 'ai';
  type: 'text' | 'error';
  metadata?: {
    queryType?: string;
    confidence?: number;
    sources?: Array<{
      type: string;
      id: number;
      title: string;
      relevance: number;
    }>;
    processingTime?: number;
  };
}

export interface ChatSession {
  id: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatSource {
  type: string;
  id: number;
  title: string;
  relevance: number;
  story_type?: string;
  event_type?: string;
  heritage_type?: string;
  person?: string;
  people?: string[];
  date?: string;
  importance?: string;
  is_hereditary?: boolean;
}

export interface ChatApiResponse {
  query: string;
  response: string;
  sources: ChatSource[];
  metadata: {
    query_type: string;
    confidence: number;
    processing_time: number;
    sources_count: number;
    language: string;
  };
}