import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

function PickupRequest() {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: user ? user.name : '',
    email: user ? user.email : '',
    phone: user ? user.phone : '',
    name: '',
    email: '',
    phone: '',
    address: '',
    pickupDate: '',
    packageType: '',
    packageWeight: '',
    specialInstructions: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        name: user.name,
        email: user.email,
        phone: user.phone
      }));
    }
  }, [user]);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    alert('Pickup request submitted successfully! We will contact you shortly.');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Request a Pickup</h1>
      <div className="bg-white rounded-lg shadow-lg p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>
          </div>

          {/* Address */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pickup Address
            </label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
          </div>

          {/* Package Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Package Type
              </label>
              <select
                name="packageType"
                value={formData.packageType}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                required
              >
                <option value="">Select package type</option>
                <option value="document">Documents</option>
                <option value="parcel">Parcel</option>
                <option value="package">Package</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Package Weight (kg)
              </label>
              <input
                type="number"
                name="packageWeight"
                value={formData.packageWeight}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                required
                min="0"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Special Instructions
              </label>
              <textarea
                name="specialInstructions"
                value={formData.specialInstructions}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Request Pickup
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PickupRequest;
