import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleSidebarToggle = () => {
    const event = new Event('sidebarToggle', { bubbles: true });
    document.dispatchEvent(event);
  };

  return (
    <header className="bg-white shadow-lg">
      <div className="max-w-8xl mx-auto px-4 sm:px-8 lg:px-12">
        <div className="flex justify-between h-20">
          <div className="flex items-center">
            <button
              className="text-gray-500 hover:text-gray-700"
              onClick={handleSidebarToggle}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            <div className="flex-shrink-0 flex items-center space-x-4">
              <Link to="/">
                <img
                  className="h-12 w-auto object-contain"
                  src="/images/pmb-logo.png"
                  alt="ParcelMyBox Logo"
                />
              </Link>
              <h1 className="ml-4 text-2xl font-bold text-indigo-900">ParcelMyBox</h1>
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
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span className="ml-2 text-sm">Cart</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
