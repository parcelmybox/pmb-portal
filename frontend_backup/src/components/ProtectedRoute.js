import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function ProtectedRoute({ children, isAdminRoute = false }) {
  const { user } = useAuth();

  if (!user.isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (isAdminRoute && !user.isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default ProtectedRoute;
