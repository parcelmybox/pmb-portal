import React, { useEffect } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  HomeIcon,
  CalculatorIcon,
  TruckIcon,
  TagIcon,
  ShoppingBagIcon,
  PhoneIcon,
  UserIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

const activeStyle = {
  backgroundColor: '#374151',
  color: '#f3f4f6',
};

export default function Sidebar({ showSidebar, setShowSidebar }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showSidebar && !e.target.closest('.sidebar')) {
        setShowSidebar(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSidebar, setShowSidebar]);

  return (
    <>
      {/* Backdrop */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-40"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`sidebar fixed top-0 left-0 h-full w-64 bg-indigo-900 text-white z-50 transform transition-transform duration-300 ${
          showSidebar ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ boxShadow: '0 2px 15px rgba(0,0,0,0.1)' }}
        role="navigation"
        onClick={(e) => e.stopPropagation()}
        aria-label="Main navigation"
        data-testid="sidebar"
      >
        <div className="flex flex-col h-full">

          {/* Sidebar Logo */}
          <div className="px-4 pt-4 pb-2 flex justify-center border-b border-gray-700">
            <Link to="/" onClick={() => setShowSidebar(false)}>
              <img
                src="/images/sidebar-logo.png"
                alt="Sidebar Logo"
                className="h-45 w-auto object-contain"
              />
            </Link>
          </div>

          <nav className="mt-6 px-3 space-y-1">
            <div className="space-y-1">
              <NavLink
                to="/"
                style={({ isActive }) => (isActive ? activeStyle : undefined)}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                onClick={() => setShowSidebar(false)}
              >
                <HomeIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Home</span>
              </NavLink>

              <NavLink
                to="/quote"
                style={({ isActive }) => (isActive ? activeStyle : undefined)}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                onClick={() => setShowSidebar(false)}
              >
                <CalculatorIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Quote</span>
              </NavLink>

              <NavLink
                to="/pickup"
                style={({ isActive }) => (isActive ? activeStyle : undefined)}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                onClick={() => setShowSidebar(false)}
              >
                <TruckIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Pickup Request</span>
              </NavLink>

              <NavLink
                to="/tracking"
                style={({ isActive }) => (isActive ? activeStyle : undefined)}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                onClick={() => setShowSidebar(false)}
              >
                <MagnifyingGlassIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Tracking</span>
              </NavLink>

              <NavLink
                to="/pricing"
                style={({ isActive }) => (isActive ? activeStyle : undefined)}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                onClick={() => setShowSidebar(false)}
              >
                <TagIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Pricing</span>
              </NavLink>
            </div>

            <div className="mt-6">
              <div className="space-y-1">
                <Link
                  to="/cart"
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                  onClick={() => setShowSidebar(false)}
                >
                  <ShoppingBagIcon className="h-5 w-5" />
                  <span className="text-sm font-medium">Cart</span>
                </Link>

                <Link
                  to="/support"
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                  onClick={() => setShowSidebar(false)}
                >
                  <PhoneIcon className="h-5 w-5" />
                  <span className="text-sm font-medium">Customer Support</span>
                </Link>

                <Link
                  to="/feedback"
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                  onClick={() => setShowSidebar(false)}
                >
                  <DocumentTextIcon className="h-5 w-5" />
                  <span className="text-sm font-medium">Customer Feedback</span>
                </Link>
              </div>

              <div className="mt-6">
                {!user?.isAuthenticated ? (
                  <Link
                    to="/auth"
                    className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                    onClick={() => setShowSidebar(false)}
                  >
                    <UserIcon className="h-5 w-5" />
                    <span className="text-sm font-medium">Sign In</span>
                  </Link>
                ) : (
                  <>
                    <NavLink
                      to="/profile"
                      style={({ isActive }) => (isActive ? activeStyle : undefined)}
                      className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                      onClick={() => setShowSidebar(false)}
                    >
                      <UserIcon className="h-5 w-5" />
                      <span className="text-sm font-medium">Profile</span>
                    </NavLink>
                    <button
                      onClick={() => {
                        handleLogout();
                        setShowSidebar(false);
                      }}
                      className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700 w-full"
                    >
                      <Cog6ToothIcon className="h-5 w-5" />
                      <span className="text-sm font-medium">Logout</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </nav>
        </div>
      </div>
    </>
  );
}
