import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { canTheme } from '../../styles/themes/canTheme';

const LanguageButton = styled.button<{ isActive: boolean }>`
  background: ${props => props.isActive ? canTheme.colors.primary : 'transparent'};
  color: ${props => props.isActive ? 'white' : canTheme.colors.primary};
  border: 1px solid ${canTheme.colors.primary};
  padding: 6px 12px;
  border-radius: ${canTheme.borderRadius.small};
  font-size: 0.9rem;
  cursor: pointer;
  transition: all ${canTheme.transitions.fast};

  &:hover {
    background: ${props => props.isActive ? canTheme.colors.primaryDark : canTheme.colors.primary}20;
  }
`;

const Container = styled.div`
  display: flex;
  gap: 8px;
`;

const languages = [
  { code: 'en', label: 'EN' },
  { code: 'fr', label: 'FR' }
];

export const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (langCode: string) => {
    i18n.changeLanguage(langCode);
    localStorage.setItem('preferred-language', langCode);
  };

  useEffect(() => {
    const storedLang = localStorage.getItem('preferred-language');
    if (storedLang && storedLang !== i18n.language) {
      changeLanguage(storedLang);
    }
  }, []);

  return (
    <Container>
      {languages.map(({ code, label }) => (
        <LanguageButton
          key={code}
          isActive={i18n.language === code}
          onClick={() => changeLanguage(code)}
        >
          {label}
        </LanguageButton>
      ))}
    </Container>
  );
};