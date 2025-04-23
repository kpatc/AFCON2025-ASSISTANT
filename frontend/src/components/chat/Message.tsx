import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { canTheme } from '../../styles/themes/canTheme';

interface MessageProps {
  content: string;
  isUser: boolean;
  timestamp: string;
  confidence?: number;
  sources?: string[];
  suggested_questions?: string[];
  onSuggestedQuestionClick?: (question: string) => void;
}

const MessageContainer = styled.div<{ isUser: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin: 8px 0;
  max-width: 85%;
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  background: ${props => props.isUser ? canTheme.colors.primary : 'white'};
  color: ${props => props.isUser ? 'white' : canTheme.colors.text};
  padding: 12px 16px;
  border-radius: ${canTheme.borderRadius.medium};
  box-shadow: ${canTheme.shadows.light};
  font-size: 0.95rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
`;

const Timestamp = styled.span`
  font-size: 0.75rem;
  color: ${canTheme.colors.textLight};
  margin-top: 4px;
`;

const MetadataContainer = styled.div`
  margin-top: 8px;
  font-size: 0.85rem;
  color: ${canTheme.colors.textLight};
`;

const ConfidenceIndicator = styled.div<{ confidence: number }>`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
`;

const ConfidenceBar = styled.div<{ confidence: number }>`
  width: 100px;
  height: 4px;
  background: ${canTheme.colors.background};
  border-radius: ${canTheme.borderRadius.small};
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    height: 100%;
    width: ${props => props.confidence * 100}%;
    background: ${props => {
      if (props.confidence > 0.7) return canTheme.colors.success;
      if (props.confidence > 0.4) return canTheme.colors.warning;
      return canTheme.colors.error;
    }};
    transition: width 0.3s ease;
  }
`;

const SourcesList = styled.div`
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`;

const SourceTag = styled.span`
  background: ${canTheme.colors.background};
  padding: 2px 8px;
  border-radius: ${canTheme.borderRadius.small};
  font-size: 0.8rem;
`;

const SuggestedQuestions = styled.div`
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const SuggestedQuestion = styled.button`
  background: transparent;
  border: 1px solid ${canTheme.colors.primary}40;
  color: ${canTheme.colors.primary};
  padding: 8px 12px;
  border-radius: ${canTheme.borderRadius.small};
  font-size: 0.9rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;

  &:hover {
    background: ${canTheme.colors.primary}10;
    border-color: ${canTheme.colors.primary};
  }
`;

export const Message: React.FC<MessageProps> = ({
  content,
  isUser,
  timestamp,
  confidence,
  sources,
  suggested_questions,
  onSuggestedQuestionClick
}) => {
  const { t } = useTranslation();
  
  return (
    <MessageContainer 
      isUser={isUser}
      role={isUser ? 'complementary' : 'region'}
      aria-label={isUser ? 'User message' : 'Assistant response'}
    >
      <MessageBubble isUser={isUser}>
        {content}
      </MessageBubble>
      <Timestamp>{timestamp}</Timestamp>
      
      {!isUser && (
        <MetadataContainer>
          {confidence !== undefined && (
            <ConfidenceIndicator confidence={confidence}>
              <span>{t('confidence')}: {Math.round(confidence * 100)}%</span>
              <ConfidenceBar 
                confidence={confidence}
                role="progressbar"
                aria-valuenow={Math.round(confidence * 100)}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </ConfidenceIndicator>
          )}
          
          {sources && sources.length > 0 && (
            <>
              <div>{t('sources')}:</div>
              <SourcesList role="list">
                {sources.map((source, index) => (
                  <SourceTag key={index} role="listitem">{source}</SourceTag>
                ))}
              </SourcesList>
            </>
          )}
          
          {suggested_questions && suggested_questions.length > 0 && (
            <SuggestedQuestions>
              <div>{t('suggested.title')}</div>
              {suggested_questions.map((question, index) => (
                <SuggestedQuestion
                  key={index}
                  onClick={() => onSuggestedQuestionClick?.(question)}
                  aria-label={`Ask: ${question}`}
                >
                  {question}
                </SuggestedQuestion>
              ))}
            </SuggestedQuestions>
          )}
        </MetadataContainer>
      )}
    </MessageContainer>
  );
};