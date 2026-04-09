import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';

export const SupabaseAuthContext = createContext();

export function SupabaseAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verificar si hay usuario en almacenamiento seguro
  useEffect(() => {
    bootstrapAsync();
  }, []);

  const bootstrapAsync = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (e) {
      console.error('Error restoring token:', e);
    } finally {
      setLoading(false);
    }
  };

  const authContext = {
    user,
    loading,
    error,

    loginAsync: async (username, password) => {
      setLoading(true);
      setError(null);
      try {
        const result = await authService.login(username, password);
        if (result.success) {
          setUser(result.user);
          return result;
        } else {
          setError(result.error);
          return result;
        }
      } catch (e) {
        const errorMessage = e.message;
        setError(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },

    registerAsync: async (username, password, nombre, foto) => {
      setLoading(true);
      setError(null);
      try {
        const result = await authService.register(
          username,
          password,
          nombre,
          foto
        );
        if (result.success) {
          return result;
        } else {
          setError(result.error);
          return result;
        }
      } catch (e) {
        const errorMessage = e.message;
        setError(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },

    logoutAsync: async () => {
      setLoading(true);
      try {
        const result = await authService.logout();
        if (result.success) {
          setUser(null);
        }
        return result;
      } finally {
        setLoading(false);
      }
    },

    addGroupToCurrentUser: async (groupId) => {
      if (!user) return { success: false, error: 'No user logged in' };
      const result = await authService.addGroupToUser(user.id, groupId);
      if (result.success) {
        const updatedUser = await authService.getCurrentUser();
        setUser(updatedUser);
      }
      return result;
    },
  };

  return (
    <SupabaseAuthContext.Provider value={authContext}>
      {children}
    </SupabaseAuthContext.Provider>
  );
}

export const useSupabaseAuth = () => {
  const context = useContext(SupabaseAuthContext);
  if (!context) {
    throw new Error(
      'useSupabaseAuth must be used within a SupabaseAuthProvider'
    );
  }
  return context;
};
