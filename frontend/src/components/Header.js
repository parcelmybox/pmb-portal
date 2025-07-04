import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bars3Icon, ShoppingCartIcon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

export default function Header({ showSidebar, setShowSidebar }) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleSidebarToggle = () => {
    console.log('Toggle clicked');
    setShowSidebar(prev => !prev);
  };

  return (
    <header className="bg-white shadow-lg">
      <div className="max-w-8xl mx-auto px-4 sm:px-8 lg:px-12">
        <div className="flex justify-between h-20">
          <div className="flex items-center">
            <button
              className="text-gray-500 hover:text-gray-700 -ml-4"
              onClick={handleSidebarToggle}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            <div className="flex-shrink-0 flex items-center space-x-4">
              <Link to="/">
                <img
                  className="h-12 max-h-14 w-auto object-contain"
                  src="/images/pmb-logo1.png"
                  alt="ParcelMyBox Logo"
                />
              </Link>
              
            </div>
          </div>

          <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
            <Link to="/" className="inline-flex items-center px-1 pt-1 border-b-2 border-indigo-500 text-sm font-medium text-indigo-900">Home</Link>
            <Link to="/quote" className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-indigo-700 hover:border-indigo-500 hover:text-indigo-900">Quote</Link>
            <Link to="/tracking" className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-indigo-700 hover:border-indigo-500 hover:text-indigo-900">Track</Link>
            <Link to="/pricing" className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-indigo-700 hover:border-indigo-500 hover:text-indigo-900">Pricing</Link>
            <Link to="/pickup" className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-indigo-700 hover:border-indigo-500 hover:text-indigo-900">Pickup Request</Link>
            <Link to="/about" className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-indigo-700 hover:border-indigo-500 hover:text-indigo-900">About</Link>
          </div>

          <div className="flex items-center">
            <Link to="/cart" className="hidden sm:ml-6 sm:flex items-center text-gray-700 hover:text-gray-900">
              <ShoppingCartIcon className="h-6 w-6" />
              <span className="ml-2 text-sm">Cart</span>
            </Link>

            <div className="ml-3 relative">
              <button
                type="button"
                className="bg-white rounded-full flex text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 hover:bg-gray-50 hover:text-indigo-600 transition-colors duration-200 ease-in-out"
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              >
                <span className="sr-only">View notifications</span>
                <BellIcon className="h-6 w-6 text-gray-400" />
              </button>

              {isNotificationsOpen && (
                <div className="origin-top-right absolute right-0 mt-2 w-80 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5">
                  <div className="border-b border-gray-200 px-4 py-3">
                    <h3 className="text-sm font-medium text-gray-900">Notifications</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      You have 3 unread messages
                    </p>
                  </div>
                  <ul className="divide-y divide-gray-200">
                    <li>
                      <a href="#" className="block px-4 py-3" onClick={() => setIsNotificationsOpen(false)}>
                        <div className="flex items-center space-x-4">
                          <div className="flex-1 w-0">
                            <p className="text-sm font-medium text-gray-900">Your shipment has been picked up</p>
                            <p className="text-sm text-gray-500">Your package is now on its way to the destination</p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500">
                            <time dateTime="2025-06-05">2 hours ago</time>
                          </div>
                        </div>
                      </a>
                    </li>
                  </ul>
                  <div className="border-t border-gray-200 px-4 py-3">
                    <a href="#" className="block text-sm font-medium text-indigo-600 hover:text-indigo-500" onClick={() => setIsNotificationsOpen(false)}>
                      View all notifications
                    </a>
                  </div>
                </div>
              )}
            </div>

            <div className="ml-3 relative">
              <button
                type="button"
                className="bg-white rounded-full flex text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 hover:bg-gray-50 hover:text-indigo-600 transition-colors duration-200 ease-in-out"
                id="user-menu-button"
                aria-expanded="false"
                aria-haspopup="true"
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              >
                <span className="sr-only">Open user menu</span>
                <UserCircleIcon className="h-6 w-6 text-gray-400" />
              </button>

              {isUserMenuOpen && (
                <div
                  className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu-button"
                >
                  {user.isAuthenticated ? (
                    <>
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setIsUserMenuOpen(false)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setIsUserMenuOpen(false);
                        }}
                      >
                        Profile
                      </Link>
                      <button
                        onClick={() => {
                          logout();
                          navigate('/');
                          setIsUserMenuOpen(false);
                        }}
                        className="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Logout
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        to="/auth"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setIsUserMenuOpen(false)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setIsUserMenuOpen(false);
                        }}
                      >
                        Sign in / Create Account
                      </Link>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}


