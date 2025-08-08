import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api'; // Use our configured axios instance

// Create the context
const AuthContext = createContext(null);

// Custom hook to use the AuthContext, which simplifies component logic
export const useAuth = () => {
  return useContext(AuthContext);
};

// The AuthProvider component that will wrap our application
export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // To handle initial user fetch

  useEffect(() => {
    const fetchUser = async () => {
      if (authToken) {
        try {
          const response = await api.get('/users/me/', {
            headers: { Authorization: `Bearer ${authToken}` },
          });
          setUser(response.data);
        } catch (error) {
          console.error("Failed to fetch user, token might be invalid", error);
          // If token is invalid, log out the user
          logout();
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, [authToken]);

  const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await api.post('/token', formData);
      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('authToken', access_token);
        setAuthToken(access_token); // This will trigger the useEffect to fetch the user
        return { success: true };
      }
      return { success: false, message: "Login succeeded but no token was provided." };
    } catch (error) {
      console.error("Login failed:", error);
      const message = error.response?.data?.detail || "An unknown error occurred.";
      return { success: false, message };
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setAuthToken(null);
    setUser(null);
  };

  // The value provided to consuming components
  const value = {
    authToken,
    user,
    isLoggedIn: !!authToken,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {/* Don't render children until the initial auth check is complete */}
      {!loading && children}
    </AuthContext.Provider>
  );
};
