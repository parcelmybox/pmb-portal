import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({ isAuthenticated: false });
  const [loading, setLoading] = useState(true);

  // Load token & fetch user on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/auth/user/');
      setUser({ ...response.data, isAuthenticated: true });
    } catch (err) {
      console.error('Error fetching user:', err);
      setUser({ isAuthenticated: false });
    } finally {
      setLoading(false);
    }
  };

  const signup = async (first_name, last_name, email, password) => {
    try {
      await axios.post('http://localhost:8000/api/auth/signup/', {
        first_name,
        last_name,
        email,
        password,
      });
      return await login(email, password); // auto login after signup
    } catch (err) {
      alert('Signup failed. Please check fields.');
      return false;
    }
  };

  const login = async (email, password) => {
    try {
      const res = await axios.post('http://localhost:8000/api/auth/token/', {
        email,
        password,
      });

      const { access, refresh } = res.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;

      await fetchUser(); // fetch user details after login
      return true;
    } catch (err) {
      alert('Login failed. Check credentials.');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete axios.defaults.headers.common['Authorization'];
    setUser({ isAuthenticated: false });
  };

  return (
    <AuthContext.Provider value={{ user, signup, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
