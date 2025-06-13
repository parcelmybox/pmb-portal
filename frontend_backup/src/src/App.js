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
import Admin from './pages/Admin';
import PickupRequest from './pages/PickupRequest';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import About from './pages/About';

function App() {
  const [showSidebar, setShowSidebar] = useState(true);

  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Header showSidebar={showSidebar} setShowSidebar={setShowSidebar} />
          <div className="flex-1 flex">
            <div className="w-64">
              <div className="h-full">
                <Sidebar showSidebar={showSidebar} setShowSidebar={setShowSidebar} />
              </div>
            </div>
            <div className="flex-1 p-4">
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
                <Route path="/admin/dashboard" element={<ProtectedRoute isAdminRoute={true}><AdminDashboard /></ProtectedRoute>} />
                <Route path="/admin" element={<ProtectedRoute isAdminRoute={true}><Admin /></ProtectedRoute>} />
              </Routes>
            </div>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}
export default App;
