import React, { useState } from 'react';

function Tracking() {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [shippingRoute, setShippingRoute] = useState('india-to-usa');
  const [trackingResults, setTrackingResults] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const handleTrack = () => {
    if (trackingNumber.trim()) {
      setTrackingResults({
        trackingNumber,
        route: shippingRoute,
        status: 'In Transit',
        lastUpdate: new Date().toISOString()
      });
      setShowResults(true);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">Track Your International Shipment</h1>
      <p className="text-gray-600 mb-6 text-center">
        Track your international shipment between India and USA. Enter your tracking number to see its current status and journey details.
      </p>
      
      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <input 
            type="radio" 
            id="india-to-usa" 
            name="shippingRoute" 
            value="india-to-usa" 
            checked={shippingRoute === 'india-to-usa'}
            onChange={(e) => setShippingRoute(e.target.value)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
          />
          <label htmlFor="india-to-usa" className="text-sm font-medium text-gray-700">India to USA</label>
        </div>
        <div className="flex items-center space-x-4">
          <input 
            type="radio" 
            id="usa-to-india" 
            name="shippingRoute" 
            value="usa-to-india" 
            checked={shippingRoute === 'usa-to-india'}
            onChange={(e) => setShippingRoute(e.target.value)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
          />
          <label htmlFor="usa-to-india" className="text-sm font-medium text-gray-700">USA to India</label>
        </div>
      </div>
      
      <div className="mt-6">
        <form onSubmit={(e) => {
          e.preventDefault();
          handleTrack();
        }} className="space-y-4">
          <div>
            <label htmlFor="trackingNumber" className="block text-sm font-medium text-gray-700">Tracking Number</label>
            <input 
              type="text" 
              name="trackingNumber" 
              id="trackingNumber" 
              value={trackingNumber} 
              onChange={(e) => setTrackingNumber(e.target.value)} 
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., PMB123456789012345678"
              required 
            />
          </div>
          <div>
            <button 
              type="submit" 
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Track Shipment
            </button>
          </div>
        </form>
      </div>

      {showResults && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Tracking Results:</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="space-y-4">
              <div>
                <span className="text-gray-600">Tracking Number:</span>
                <br />
                <span className="text-indigo-600 font-bold">{trackingResults.trackingNumber}</span>
              </div>
              <div>
                <span className="text-gray-600">Route:</span>
                <br />
                <span className="text-gray-900 font-medium">{trackingResults.route === 'india-to-usa' ? 'India to USA' : 'USA to India'}</span>
              </div>
              <div>
                <span className="text-gray-600">Status:</span>
                <br />
                <span className="text-blue-600 font-bold">{trackingResults.status}</span>
              </div>
              <div>
                <span className="text-gray-600">Last Update:</span>
                <br />
                <span className="text-gray-900">{new Date(trackingResults.lastUpdate).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Tracking;
