import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  UserGroupIcon,
  ChartBarIcon,
  EnvelopeIcon,
  TruckIcon,
  CogIcon
} from '@heroicons/react/24/outline';

function Admin() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user?.isAdmin) {
    navigate('/');
    return null;
  }

  const stats = {
    totalCustomers: 125,
    activeShipments: 45,
    totalRevenue: '₹2,500,000',
    pendingInquiries: 15
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <div className="mt-4">
          <button
            onClick={logout}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Logout
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Customers</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.totalCustomers}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TruckIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Shipments</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.activeShipments}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.totalRevenue}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <EnvelopeIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Pending Inquiries</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.pendingInquiries}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Shipments</h2>
          <div className="space-y-4">
            {/* Mock shipment data */}
            {[1, 2, 3, 4].map((id) => (
              <div key={id} className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Shipment #{id}</h3>
                  <p className="text-sm text-gray-500">Customer: John Doe</p>
                  <p className="text-sm text-gray-500">Status: In Transit</p>
                </div>
                <div>
                  <button className="text-sm text-indigo-600 hover:text-indigo-900">View Details</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Pending Actions</h2>
          <div className="space-y-4">
            {/* Mock pending actions */}
            {[1, 2, 3].map((id) => (
              <div key={id} className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Action #{id}</h3>
                  <p className="text-sm text-gray-500">Customer Support</p>
                  <p className="text-sm text-gray-500">Priority: High</p>
                </div>
                <div>
                  <button className="text-sm text-indigo-600 hover:text-indigo-900">Resolve</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Admin;
