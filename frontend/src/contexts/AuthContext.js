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
    // Temporary hardcoded logic (until backend integration)
    const isAdmin = email === 'admin@parcelmybox.com';
    const validUser = email && password; // simple check

    if (!validUser) {
      alert("Please enter valid credentials");
      return false;
    }

    setUser({
      isAuthenticated: true,
      isAdmin,
      name: isAdmin ? 'Admin User' : email.split('@')[0],
      email
    });
    return true;
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
