export interface ChatMessage {
  content: string;
  role: string;
  language?: string;
}

export interface ChatResponse {
  response: string;
  error?: string;
  confidence: number;
  sources: string[];
  categories: string[];
  suggested_questions: string[];
}

export interface UIMessage extends ChatMessage {
  id: number;
  isUser: boolean;
  timestamp: string;
  confidence?: number;
  sources?: string[];
  suggested_questions?: string[];
}