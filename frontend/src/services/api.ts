import { ChatMessage, ChatResponse } from '../types/chat';
import i18n from '../config/i18n';

const API_BASE_URL = 'http://localhost:8000';

const getErrorMessage = (error: any): string => {
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error?.message?.includes('Failed to fetch')) {
    return i18n.t('errors.connection');
  }
  
  if (error?.message?.includes('timeout')) {
    return i18n.t('errors.timeout');
  }
  
  return i18n.t('errors.unknown');
};

export const chatService = {
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept-Language': i18n.language
        },
        body: JSON.stringify({
          content: message,
          role: 'user',
          language: i18n.language
        } as ChatMessage),
      });

      const data = await response.json();
      
      if (!response.ok) {
        return {
          response: i18n.t('errors.server', { message: data.detail || i18n.t('errors.unknown') }),
          error: data.detail,
          confidence: 0,
          sources: [],
          categories: [],
          suggested_questions: []
        };
      }

      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      return {
        response: getErrorMessage(error),
        error: error instanceof Error ? error.message : "Unknown error",
        confidence: 0,
        sources: [],
        categories: [],
        suggested_questions: []
      };
    }
  },

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        console.error('Health check failed:', await response.text());
        return false;
      }
      const data = await response.json();
      return data.status === 'healthy' && 
             Object.values(data.components).every(status => status === 'operational');
    } catch (error) {
      console.error('Health check error:', error);
      return false;
    }
  }
};