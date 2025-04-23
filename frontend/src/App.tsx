import React, { Suspense } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { Auth0Provider } from '@auth0/auth0-react';
import { AuthProvider } from './context/AuthContext';
import { ChatContainer } from './components/chat/ChatContainer';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { Loading } from './components/common/Loading';
import { canTheme } from './styles/themes/canTheme';
import { auth0Config } from './config/auth0-config';
import './config/i18n';
import './App.css';

const AppWrapper = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, 
    ${canTheme.colors.primary}, 
    ${canTheme.colors.secondary});
  padding: 1rem;
  overflow: hidden;

  @media (max-width: 768px) {
    padding: 0.5rem;
  }
`;

const MainContent = styled.div`
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 1rem;
  color: white;

  @media (max-width: 768px) {
    margin-bottom: 0.5rem;
  }
`;

const Title = styled.h1`
  font-family: ${canTheme.fonts.secondary};
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: white;

  @media (max-width: 768px) {
    font-size: 1.8rem;
  }
`;

const Subtitle = styled.p`
  font-family: ${canTheme.fonts.primary};
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);

  @media (max-width: 768px) {
    font-size: 1rem;
  }
`;

function App() {
  return (
    <Auth0Provider {...auth0Config}>
      <AuthProvider>
        <ThemeProvider theme={canTheme}>
          <AppWrapper>
            <Header>
              <Title>Welcome to CAN 2025 Assistant</Title>
              <Subtitle>Your guide for the Africa Cup of Nations in Morocco</Subtitle>
            </Header>
            <MainContent>
              <ErrorBoundary>
                <Suspense fallback={<Loading type="processing" />}>
                  <ChatContainer />
                </Suspense>
              </ErrorBoundary>
            </MainContent>
          </AppWrapper>
        </ThemeProvider>
      </AuthProvider>
    </Auth0Provider>
  );
}

export default App;
