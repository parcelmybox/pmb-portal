import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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
import Feedback from './pages/Feedback';
import Admin from './pages/Admin';
import PickupRequest from './pages/PickupRequest';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import About from './pages/About';
import QuotePricing from './pages/QuotePricing';

function App() {
  const [showSidebar, setShowSidebar] = useState(false);

  return (
    <AuthProvider>
      <Router>
        <div className="relative min-h-screen flex flex-col">
          {/* Header */}
          <Header showSidebar={showSidebar} setShowSidebar={setShowSidebar} />

          {/* Sidebar Overlay - now conditionally rendered */}
          {showSidebar && (
            <Sidebar showSidebar={showSidebar} setShowSidebar={setShowSidebar} />
          )}

          {/* Backdrop when Sidebar is open */}
          {showSidebar && (
            <div
              className="fixed inset-0 bg-black opacity-30 z-40"
              onClick={() => setShowSidebar(false)}
            />
          )}

          {/* Main Content */}
          <div className="flex-1 p-4 pt-20 z-0">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/quote" element={<Quote />} />
              <Route path="/pickup" element={<PickupRequest />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/support" element={<Support />} />
              <Route path="/about" element={<About />} />
              <Route path="/tracking" element={<Tracking />} />
              <Route path="/feedback" element={<Feedback />} />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />
              <Route path="/auth" element={<Auth />} />
              <Route path="/create-account" element={<CreateAccount />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute isAdminRoute={true}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute isAdminRoute={true}>
                    <Admin />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/quote-result"
                element={<QuotePricing />}
              />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
