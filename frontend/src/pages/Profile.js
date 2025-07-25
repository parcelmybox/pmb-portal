import React from 'react';
import { useAuth } from '../contexts/AuthContext';

function Profile() {
  const { user } = useAuth();

  if (!user.isAuthenticated) {
    return <div className="p-6 text-center text-lg">Please sign in to view your profile.</div>;
  }

  // Static dummy values
  const phone = '+91-9848012345';
  const email = 'tonystark@gmail.com';
  const location = 'River view Heights, River street, Anna Nagar, Chennai, India';
  const lockerCode = '#1056';
  const pickupRequests = 3;

  return (
    <div className="min-h-screen bg-cover bg-center flex items-center justify-center px-6 py-10" style={{ backgroundImage: 'url(/images/container-bg.jpg)' }}>
      <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Left Profile Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center flex flex-col items-center">
          <div className="h-20 w-20 rounded-full bg-gradient-to-br from-purple-600 to-pink-500 flex items-center justify-center text-white text-3xl font-semibold shadow-lg mb-4">
            {user.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <h2 className="text-xl font-bold text-gray-800">{user.name || 'Tony Stark'}</h2>
          <p className="text-sm text-gray-500 mb-6">@pmb{Math.floor(1000 + Math.random() * 9000)}</p>

          <div className="w-full text-left text-sm text-gray-700 space-y-2">
            <p><strong>Mobile:</strong> {phone}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Location:</strong><br />{location}</p>
          </div>

          <button className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-md shadow">
            Edit Profile
          </button>
        </div>

        {/* Right Stats Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col justify-between">
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="text-center">
              <p className="text-sm text-gray-500">Locker Code</p>
              <p className="text-xl font-bold text-gray-800">{lockerCode}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Total Pickup Requests</p>
              <p className="text-xl font-bold text-gray-800">{pickupRequests}</p>
            </div>
          </div>

          <hr className="my-4" />

          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Current & Past Delivery</h3>
            <p className="text-sm text-gray-600">Details and Status Updates</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
