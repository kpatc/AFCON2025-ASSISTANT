import { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Message } from './Message';
import { ChatInput } from './ChatInput';
import { Loading } from '../common/Loading';
import { LanguageSelector } from '../common/LanguageSelector';
import { useAuth } from '../../context/AuthContext';
import { canTheme } from '../../styles/themes/canTheme';
import { chatService } from '../../services/api';
import { UIMessage } from '../../types/chat';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: ${canTheme.borderRadius.large};
  box-shadow: ${canTheme.shadows.strong};
  overflow: hidden;

  @media (max-width: 768px) {
    border-radius: ${canTheme.borderRadius.medium};
  }
`;

const Header = styled.div`
  background: ${canTheme.colors.primary};
  color: white;
  padding: 16px;
  text-align: center;
  font-family: ${canTheme.fonts.secondary};
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
`;

const AuthButton = styled.button`
  background: #4A148C;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: ${canTheme.borderRadius.small};
  cursor: pointer;
  font-family: ${canTheme.fonts.primary};
  margin-left: 12px;
  
  &:hover {
    background: #6a1b9a;
  }
`;

const MessagesArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  background: ${canTheme.colors.background};
`;

const ScrollableMessages = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column-reverse;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: ${canTheme.colors.primary}40;
    border-radius: 4px;
  }
`;

const MessagesContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-height: min-content;
`;

const InputWrapper = styled.div`
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 16px;
`;

type LoadingState = 'thinking' | 'searching' | 'processing' | null;

export const ChatContainer = () => {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>(null);
  const { t } = useTranslation();
  const { isAuthenticated, login, logout } = useAuth();

  useEffect(() => {
    const welcomeMessage: UIMessage = {
      id: Date.now(),
      content: t('welcome') + '\n\n' +
              t('features.matches') + '\n' +
              t('features.hotels') + '\n' +
              t('features.restaurants') + '\n' +
              t('features.health') + '\n' +
              t('features.transport') + '\n\n' +
              t('ask'),
      isUser: false,
      role: 'assistant',
      timestamp: new Date().toLocaleTimeString(),
      confidence: 1.0,
      sources: ['System'],
      suggested_questions: [
        t('suggested.matches'),
        t('suggested.hotels'),
        t('suggested.transport')
      ]
    };
    setMessages([welcomeMessage]);
  }, [t]);

  const handleSuggestedQuestionClick = (question: string) => {
    handleSendMessage(question);
  };

  const handleSendMessage = async (content: string) => {
    const newUserMessage: UIMessage = {
      id: Date.now(),
      content,
      isUser: true,
      role: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, newUserMessage]);
    
    // Séquence de chargement
    setLoadingState('thinking');
    setTimeout(() => setLoadingState('searching'), 1000);
    setTimeout(() => setLoadingState('processing'), 2000);

    try {
      const data = await chatService.sendMessage(content);
      
      const botMessage: UIMessage = {
        id: Date.now(),
        content: data.response,
        isUser: false,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        confidence: data.confidence,
        sources: data.sources,
        suggested_questions: data.suggested_questions
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Scroll to the latest message smoothly
      setTimeout(() => {
        const messagesContainer = document.querySelector('.messages-scroll');
        if (messagesContainer) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
      }, 100);

    } catch (error) {
      const errorMessage: UIMessage = {
        id: Date.now(),
        content: t('error'),
        isUser: false,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        confidence: 0,
        sources: ['Error']
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Chat error:', error);
    } finally {
      setLoadingState(null);
    }
  };

  return (
    <Container>
      <Header>
        <HeaderContent>
          <span>CAN 2025 Assistant - Morocco</span>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <LanguageSelector />
            <AuthButton onClick={isAuthenticated ? logout : login}>
              {isAuthenticated ? t('logout') : t('login')}
            </AuthButton>
          </div>
        </HeaderContent>
      </Header>
      <MessagesArea>
        <ScrollableMessages className="messages-scroll">
          <MessagesContainer>
            {messages.map((message) => (
              <Message
                key={message.id}
                content={message.content}
                isUser={message.isUser}
                timestamp={message.timestamp}
                confidence={message.confidence}
                sources={message.sources}
                suggested_questions={message.suggested_questions}
                onSuggestedQuestionClick={handleSuggestedQuestionClick}
              />
            ))}
            {loadingState && <Loading type={loadingState} />}
          </MessagesContainer>
        </ScrollableMessages>
      </MessagesArea>
      <InputWrapper>
        <ChatInput 
          onSendMessage={handleSendMessage} 
          isLoading={loadingState !== null} 
        />
      </InputWrapper>
    </Container>
  );
};