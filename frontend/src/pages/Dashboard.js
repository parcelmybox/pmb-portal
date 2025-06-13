import React from 'react';
import { Link } from 'react-router-dom'; // Import Link for navigation

function Dashboard() {
  const cardClass = "bg-white shadow-lg rounded-lg p-6 hover:shadow-xl transition-shadow duration-300 ease-in-out";
  const linkClass = "text-indigo-600 hover:text-indigo-800 font-semibold";

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to ParcelMyBox</h1>
      <p className="text-gray-600">
        Manage your international shipments between India and USA. Get quotes, track parcels, and manage your shipping needs.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Card 1: Request a Quote */}
        <div className={cardClass}>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Get a Shipping Quote</h2>
          <p className="text-gray-600 mb-4">
            Get an estimate for shipping between India and USA. Choose from standard or priority shipping options.
          </p>
          <Link to="/quote" className={linkClass}>
            Request a Quote &rarr;
          </Link>
        </div>

        {/* Card 2: Track a Parcel */}
        <div className={cardClass}>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Track Your International Shipment</h2>
          <p className="text-gray-600 mb-4">
            Track your international shipments between India and USA. Get real-time updates on your parcel's journey.
          </p>
          <Link to="/tracking" className={linkClass}>
            Track a Parcel &rarr;
          </Link>
        </div>
        
        {/* Card 3: View Profile (Example) */}
        <div className={cardClass}>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Your Profile</h2>
          <p className="text-gray-600 mb-4">
            Manage your account settings and preferences.
          </p>
          <Link to="/profile" className={linkClass}>
            Go to Profile &rarr;
          </Link>
        </div>
      </div>
      
      <div className="mt-10">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Recent Activity</h2>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-gray-500">No recent activity to display yet.</p>
        </div>
      </div>
    </div>
  );
}
export default Dashboard;
