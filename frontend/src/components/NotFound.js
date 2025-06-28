import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-4">
    <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
    <h2 className="text-2xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
    <p className="text-gray-600 mb-6">The page you're looking for doesn't exist or has been moved.</p>
    <Link 
      to="/" 
      className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
    >
      Go to Home
    </Link>
  </div>
);

export default NotFound;
