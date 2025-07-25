import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState({
    isAuthenticated: false,
    isAdmin: false,
    name: '',
    email: ''
  });

  const login = async (email, password) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      const { access, refresh } = data;

      // Store both tokens in localStorage
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      // Update user state
      setUser({
        isAuthenticated: true,
        isAdmin: email === 'admin@parcelmybox.com',
        name: email.split('@')[0],
        email
      });

      return true;
    } catch (error) {
      alert("Invalid credentials");
      return false;
    }
  };

  const signup = async (name, email, password) => {
    if (!name || !email || !password) {
      alert("All fields are required");
      return false;
    }

    // Temporary placeholder logic
    setUser({
      isAuthenticated: true,
      isAdmin: false,
      name,
      email
    });
    return true;
  };

  const logout = () => {
    // Clear tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser({
      isAuthenticated: false,
      isAdmin: false,
      name: '',
      email: ''
    });
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
