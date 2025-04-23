import { Component, ErrorInfo, ReactNode } from 'react';
import styled from 'styled-components';
import { withTranslation, WithTranslation } from 'react-i18next';
import { canTheme } from '../../styles/themes/canTheme';

interface Props extends WithTranslation {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

const ErrorContainer = styled.div`
  padding: 20px;
  margin: 10px;
  background-color: ${canTheme.colors.background};
  border: 1px solid ${canTheme.colors.error};
  border-radius: ${canTheme.borderRadius.medium};
  color: ${canTheme.colors.error};
`;

const ResetButton = styled.button`
  margin-top: 10px;
  padding: 8px 16px;
  background-color: ${canTheme.colors.primary};
  color: white;
  border: none;
  border-radius: ${canTheme.borderRadius.small};
  cursor: pointer;
  
  &:hover {
    background-color: ${canTheme.colors.primaryDark};
  }
`;

class ErrorBoundaryComponent extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by error boundary:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null
    });
  };

  public render() {
    const { t } = this.props;
    
    if (this.state.hasError) {
      return (
        <ErrorContainer role="alert">
          <h3>{t('errors.title')}</h3>
          <p>{t('errors.message')}</p>
          {this.state.error && (
            <p>
              <small>{this.state.error.message}</small>
            </p>
          )}
          <ResetButton onClick={this.handleReset}>
            {t('errors.reset')}
          </ResetButton>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export const ErrorBoundary = withTranslation()(ErrorBoundaryComponent);