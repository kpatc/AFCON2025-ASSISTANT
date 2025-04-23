import React from 'react';
import styled, { keyframes } from 'styled-components';
import { useTranslation } from 'react-i18next';
import { canTheme } from '../../styles/themes/canTheme';

interface LoadingProps {
  type?: 'thinking' | 'searching' | 'processing';
}

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: ${canTheme.colors.background};
  border-radius: ${canTheme.borderRadius.medium};
  max-width: fit-content;
`;

const Spinner = styled.div`
  width: 24px;
  height: 24px;
  border: 3px solid ${canTheme.colors.primary}20;
  border-top: 3px solid ${canTheme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const Text = styled.span`
  color: ${canTheme.colors.text};
  font-size: 0.9rem;
  font-family: ${canTheme.fonts.primary};
`;

const getLoadingMessage = (type: LoadingProps['type'], t: any) => {
  switch (type) {
    case 'thinking':
      return t('loading.thinking');
    case 'searching':
      return t('loading.searching');
    case 'processing':
      return t('loading.processing');
    default:
      return t('loading.default');
  }
};

export const Loading: React.FC<LoadingProps> = ({ type = 'thinking' }) => {
  const { t } = useTranslation();
  const message = getLoadingMessage(type, t);
  
  return (
    <Container role="alert" aria-live="polite" aria-busy="true">
      <Spinner aria-hidden="true" />
      <Text>{message}</Text>
    </Container>
  );
};