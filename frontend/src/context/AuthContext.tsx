import { createContext, useContext, ReactNode } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any;
  login: () => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const {
    isAuthenticated,
    user,
    loginWithRedirect,
    logout: auth0Logout,
    isLoading,
  } = useAuth0();

  const login = () => loginWithRedirect();
  const logout = () => auth0Logout({ logoutParams: { returnTo: window.location.origin } });

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};