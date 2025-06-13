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
    // TODO: Implement actual authentication logic
    const isAdmin = email === 'admin@parcelmybox.com';
    setUser({
      isAuthenticated: true,
      isAdmin,
      name: isAdmin ? 'Admin User' : email.split('@')[0],
      email: email
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
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}


