import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { canTheme } from '../../styles/themes/canTheme';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const InputContainer = styled.div`
  display: flex;
  gap: 12px;
  width: 100%;
  position: relative;
`;

const StyledTextarea = styled.textarea<{ hasValue: boolean }>`
  flex: 1;
  padding: 12px;
  padding-right: ${props => props.hasValue ? '48px' : '12px'};
  border: 2px solid ${canTheme.colors.primary}40;
  border-radius: ${canTheme.borderRadius.medium};
  font-family: ${canTheme.fonts.primary};
  font-size: 0.95rem;
  resize: none;
  min-height: 48px;
  max-height: 120px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${canTheme.colors.primary};
  }

  &::placeholder {
    color: ${canTheme.colors.textLight};
  }

  &:disabled {
    background: ${canTheme.colors.background};
    cursor: not-allowed;
    opacity: 0.7;
  }
`;

const SendButton = styled.button<{ visible: boolean }>`
  position: absolute;
  right: 8px;
  bottom: 8px;
  background: ${canTheme.colors.primary};
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: ${props => props.visible ? 1 : 0};
  transform: scale(${props => props.visible ? 1 : 0.8});
  pointer-events: ${props => props.visible ? 'auto' : 'none'};

  &:hover:not(:disabled) {
    background: ${canTheme.colors.primaryDark};
    transform: scale(${props => props.visible ? 1.1 : 0.8});
  }

  &:disabled {
    background: ${canTheme.colors.textLight};
    cursor: not-allowed;
    transform: scale(1);
  }

  svg {
    width: 18px;
    height: 18px;
    fill: currentColor;
  }
`;

const SendIcon = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
  </svg>
);

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { t } = useTranslation();

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'inherit';
      const computed = window.getComputedStyle(textarea);
      const height = parseInt(computed.getPropertyValue('border-top-width'), 10)
                   + parseInt(computed.getPropertyValue('padding-top'), 10)
                   + textarea.scrollHeight
                   + parseInt(computed.getPropertyValue('padding-bottom'), 10)
                   + parseInt(computed.getPropertyValue('border-bottom-width'), 10);

      textarea.style.height = `${Math.min(height, 120)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = '48px';
      }
    }
  };

  return (
    <InputContainer>
      <StyledTextarea
        ref={textareaRef}
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={t(isLoading ? 'input.waiting' : 'input.placeholder')}
        disabled={isLoading}
        hasValue={message.length > 0}
        rows={1}
        aria-label={t('input.placeholder')}
      />
      <SendButton
        onClick={handleSubmit}
        disabled={!message.trim() || isLoading}
        visible={message.length > 0}
        title={t('input.send')}
        aria-label={t('input.send')}
      >
        <SendIcon />
      </SendButton>
    </InputContainer>
  );
};