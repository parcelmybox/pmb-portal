import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Auth from './pages/Auth';
import CreateAccount from './pages/CreateAccount';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import Dashboard from './pages/Dashboard';
import Quote from './pages/Quote';
import Tracking from './pages/Tracking';
import Pricing from './pages/Pricing';
import Cart from './pages/Cart';
import Support from './pages/Support';
import Profile from './pages/Profile';
import Admin from './pages/Admin';
import PickupRequest from './pages/PickupRequest';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import About from './pages/About';
import NotFound from './components/NotFound'; // Default import

// Main App component that wraps everything with Router and AuthProvider
function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

// Separate component that uses useLocation
function AppContent() {
  const [showSidebar, setShowSidebar] = useState(false);
  const location = useLocation();

  // Disable scroll when sidebar is open
  useEffect(() => {
    document.body.style.overflow = showSidebar ? 'hidden' : 'auto';
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [showSidebar]);

  // Close sidebar on route change
  useEffect(() => {
    setShowSidebar(false);
  }, [location]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      const sidebar = document.querySelector('.sidebar');
      const toggle = document.querySelector('[aria-label="Toggle menu"]');
      if (
        showSidebar &&
        sidebar &&
        !sidebar.contains(e.target) &&
        toggle &&
        !toggle.contains(e.target)
      ) {
        setTimeout(() => setShowSidebar(false), 100);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSidebar]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header showSidebar={showSidebar} setShowSidebar={setShowSidebar} />

      <div className="flex-1 flex flex-col w-full">
        {/* Overlay background */}
        {showSidebar && (
          <div
            className="fixed inset-0 bg-black bg-opacity-40 z-30"
            onClick={() => setShowSidebar(false)}
          />
        )}

        {/* Sidebar overlay (toggle on all screen sizes) */}
        {showSidebar && (
          <Sidebar showSidebar={showSidebar} setShowSidebar={setShowSidebar} />
        )}

        {/* Main content */}
        <main className="flex-1 w-full z-10 px-4">
          <div className="max-w-7xl mx-auto w-full">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/quote" element={<Quote />} />
              <Route path="/pickup" element={<PickupRequest />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/support" element={<Support />} />
              <Route path="/about" element={<About />} />
              <Route path="/tracking" element={<Tracking />} />
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />
              <Route path="/auth" element={<Auth />} />
              <Route path="/create-account" element={<CreateAccount />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin/dashboard" element={
                <ProtectedRoute isAdminRoute={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="/admin" element={
                <ProtectedRoute isAdminRoute={true}>
                  <Admin />
                </ProtectedRoute>
              } />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
