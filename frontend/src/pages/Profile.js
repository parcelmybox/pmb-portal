import React from 'react';
import { useAuth } from '../contexts/AuthContext';

function Profile() {
  const { user } = useAuth();

  if (!user.isAuthenticated) {
    return <div className="p-6 text-center">Please sign in to view your profile.</div>;
  }

  const infoRowClass = "py-3 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6";
  const labelClass = "text-sm font-medium text-gray-500";
  const valueClass = "mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2";
  const buttonClass = "mt-4 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500";

  // Temporary static values for now
  const phone = "+91-9876543210";
  const lockerCode = "PMB-98765";
  const warehouseAddress = "ParcelMyBox Warehouse, Hyderabad, Telangana";
  const totalPickupRequests = 3;
  const totalBills = 2;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">{user.isAdmin ? 'Admin Profile' : 'Your Profile'}</h1>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Account Information
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            {user.isAdmin 
              ? 'Admin account details and settings.' 
              : 'Personal details and application settings.'}
          </p>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className={`${infoRowClass} bg-gray-50`}>
              <dt className={labelClass}>Full Name</dt>
              <dd className={valueClass}>{user.name}</dd>
            </div>
            <div className={infoRowClass}>
              <dt className={labelClass}>Email Address</dt>
              <dd className={valueClass}>{user.email}</dd>
            </div>
            <div className={`${infoRowClass} bg-gray-50`}>
              <dt className={labelClass}>Phone Number</dt>
              <dd className={valueClass}>{phone}</dd>
            </div>
            <div className={infoRowClass}>
              <dt className={labelClass}>Locker Code</dt>
              <dd className={valueClass}>{lockerCode}</dd>
            </div>
            <div className={`${infoRowClass} bg-gray-50`}>
              <dt className={labelClass}>Warehouse Address</dt>
              <dd className={valueClass}>{warehouseAddress}</dd>
            </div>
            <div className={infoRowClass}>
              <dt className={labelClass}>Total Pickup Requests</dt>
              <dd className={valueClass}>{totalPickupRequests}</dd>
            </div>
            <div className={`${infoRowClass} bg-gray-50`}>
              <dt className={labelClass}>Total Bills</dt>
              <dd className={valueClass}>{totalBills}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="mt-8">
        <button type="button" className={buttonClass}>
          Edit Profile
        </button>
      </div>

      <div className="mt-10 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Security Settings
          </h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <button type="button" className={buttonClass.replace('mt-4', '')}>
            Change Password
          </button>
        </div>
      </div>
    </div>
  );
}

export default Profile;
