import React from 'react';
import { Link } from 'react-router-dom';

function About() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Your Gateway to Effortless Global Shipping
        </h1>
        <p className="text-xl text-gray-600 mx-auto max-w-2xl">
          Choose reliability, choose convenience, choose us for international courier services from India to USA.
        </p>
      </div>

      {/* Mission Statement */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Our Mission</h2>
        <p className="text-gray-600 leading-relaxed">
          At ParcelMyBox, we're dedicated to providing premium international shipping services that connect India with the USA. Our mission is to make global shipping simple, reliable, and accessible to everyone.
        </p>
      </div>

      {/* Key Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Reliability */}
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Reliability</h3>
          <p className="text-gray-600">Track your packages in real-time with our advanced tracking system</p>
        </div>

        {/* Convenience */}
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Convenience</h3>
          <p className="text-gray-600">Easy online booking and management of your shipments</p>
        </div>

        {/* Global Reach */}
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Global Reach</h3>
          <p className="text-gray-600">Seamless shipping between India and USA</p>
        </div>
      </div>

      {/* Call to Action */}
      <div className="mt-12">
        <Link
          to="/quote"
          className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Get a Quote
        </Link>
      </div>
    </div>
  );
}

export default About;
