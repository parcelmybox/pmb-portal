import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bars3Icon, ShoppingCartIcon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

export default function Header({ showSidebar, setShowSidebar }) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleSidebarToggle = () => {
    setShowSidebar(!showSidebar);
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-10">
      <div className="max-w-8xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
              onClick={handleSidebarToggle}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            <div className="flex-shrink-0 flex items-center ml-4">
              <Link to="/" className="flex items-center">
                <img
                  className="h-8 w-auto"
                  src="/images/pmb-logo.png"
                  alt="ParcelMyBox"
                />
                <span className="ml-2 text-xl font-semibold text-gray-900 hidden sm:block">ParcelMyBox</span>
              </Link>
            </div>
          </div>

          <div className="hidden md:ml-6 md:flex md:space-x-1">
            <Link to="/" className="border-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium">
              Home
            </Link>
            <Link to="/quote" className="border-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium">
              Quote
            </Link>
            <Link to="/tracking" className="border-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium">
              Track
            </Link>
            <Link to="/pricing" className="border-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium">
              Pricing
            </Link>
            <Link to="/pickup" className="border-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium">
              Pickup
            </Link>
            <Link to="/about" className="border-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium">
              About
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <Link to="/cart" className="p-1 rounded-full text-gray-500 hover:text-gray-700 hover:bg-gray-100">
              <span className="sr-only">View cart</span>
              <ShoppingCartIcon className="h-6 w-6" />
            </Link>
            
            <button
              type="button"
              className="p-1 rounded-full text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            >
              <span className="sr-only">View notifications</span>
              <BellIcon className="h-6 w-6" />
            </button>

            <div className="ml-2 relative">
              <button
                type="button"
                className="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                aria-expanded={isUserMenuOpen}
                aria-haspopup="true"
              >
                <span className="sr-only">Open user menu</span>
                <UserCircleIcon className="h-8 w-8 text-gray-400" />
              </button>

              {isUserMenuOpen && (
                <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 py-1 z-20">
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsUserMenuOpen(false)}
                  >
                    Your Profile
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      navigate('/');
                      setIsUserMenuOpen(false);
                    }}
                    className="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
