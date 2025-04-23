const canTheme = {
  colors: {
    primary: '#008751', // Vert du drapeau marocain
    primaryDark: '#006B3F',
    secondary: '#C1272D', // Rouge du drapeau marocain
    secondaryLight: '#E35D64',
    background: '#F5F5F5',
    surface: '#FFFFFF',
    text: '#1A1A1A',
    textLight: '#757575',
    error: '#D32F2F',
    success: '#2E7D32',
    warning: '#F57C00',
    info: '#1976D2'
  },
  fonts: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    secondary: "'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
  },
  borderRadius: {
    small: '4px',
    medium: '8px',
    large: '16px',
    xl: '24px'
  },
  shadows: {
    light: '0 2px 4px rgba(0,0,0,0.1)',
    medium: '0 4px 8px rgba(0,0,0,0.1)',
    strong: '0 8px 16px rgba(0,0,0,0.1)'
  },
  breakpoints: {
    mobile: '320px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px'
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px'
  },
  transitions: {
    fast: '0.2s ease',
    normal: '0.3s ease',
    slow: '0.5s ease'
  }
} as const;

export { canTheme };