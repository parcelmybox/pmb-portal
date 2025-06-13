import React from 'react';

function Pricing() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">International Shipping Pricing</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">Basic International</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-gray-600">India to USA</span>
                <br />
                <span className="text-indigo-600 font-bold text-2xl">₹4,999</span>
                <br />
                <span className="text-gray-500">$60.60</span>
              </div>
              <div>
                <span className="text-gray-600">USA to India</span>
                <br />
                <span className="text-indigo-600 font-bold text-2xl">₹7,999</span>
                <br />
                <span className="text-gray-500">$96.96</span>
              </div>
            </div>
          </div>
          <ul className="space-y-4 text-gray-600">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Standard international shipping
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Tracking included
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Insurance up to ₹10,000
            </li>
          </ul>
          <button className="mt-6 w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700">
            Get Started
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-indigo-600">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">Premium International</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-gray-600">India to USA</span>
                <br />
                <span className="text-indigo-600 font-bold text-2xl">₹8,999</span>
                <br />
                <span className="text-gray-500">$109.10</span>
              </div>
              <div>
                <span className="text-gray-600">USA to India</span>
                <br />
                <span className="text-indigo-600 font-bold text-2xl">₹14,999</span>
                <br />
                <span className="text-gray-500">$181.81</span>
              </div>
            </div>
          </div>
          <ul className="space-y-4 text-gray-600">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Priority international shipping
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Real-time tracking
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Insurance up to ₹50,000
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Priority customer support
            </li>
          </ul>
          <button className="mt-6 w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700">
            Upgrade Now
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">Enterprise International</h3>
          <p className="text-4xl font-bold text-indigo-600 mb-4">Custom</p>
          <p className="text-gray-600 mb-6">Contact us for international shipping pricing</p>
          <ul className="space-y-4 text-gray-600">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Delivery times and estimates may vary.
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Custom shipping solutions
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Priority handling
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Advanced analytics
            </li>
          </ul>
          <button className="mt-6 w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700">
            Contact Us
          </button>
        </div>
      </div>
    </div>
  );
}

export default Pricing;
