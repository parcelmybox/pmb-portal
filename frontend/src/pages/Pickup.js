import React, { useState } from 'react';

function Pickup() {
  const [formData, setFormData] = useState({
    shippingRoute: 'india-to-usa',
    pickupAddress: '',
    pickupDate: '',
    pickupTime: '',
    contactName: '',
    contactPhone: '',
    specialInstructions: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement pickup request submission
    console.log('Pickup Request Data:', formData);
    alert('Pickup request submitted! We will contact you soon.');
  };

  const inputClass = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
  const labelClass = "block text-sm font-medium text-gray-700";

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Request Pickup</h1>
      <p className="text-gray-600 mb-6">
        Schedule a pickup for your international shipment
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <input type="radio" id="india-to-usa" name="shippingRoute" value="india-to-usa" 
                   checked={formData.shippingRoute === 'india-to-usa'}
                   onChange={(e) => setFormData({...formData, shippingRoute: e.target.value})}
                   className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
            <label htmlFor="india-to-usa" className="text-sm font-medium text-gray-700">India to USA</label>
          </div>
          <div className="flex items-center space-x-4">
            <input type="radio" id="usa-to-india" name="shippingRoute" value="usa-to-india" 
                   checked={formData.shippingRoute === 'usa-to-india'}
                   onChange={(e) => setFormData({...formData, shippingRoute: e.target.value})}
                   className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
            <label htmlFor="usa-to-india" className="text-sm font-medium text-gray-700">USA to India</label>
          </div>
        </div>

        <div>
          <label htmlFor="pickupAddress" className={labelClass}>Pickup Address</label>
          <textarea
            name="pickupAddress"
            id="pickupAddress"
            rows="3"
            value={formData.pickupAddress}
            onChange={handleChange}
            className={inputClass}
            placeholder="Enter your complete address"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="pickupDate" className={labelClass}>Preferred Pickup Date</label>
            <input
              type="date"
              name="pickupDate"
              id="pickupDate"
              value={formData.pickupDate}
              onChange={handleChange}
              className={inputClass}
              required
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div>
            <label htmlFor="pickupTime" className={labelClass}>Preferred Pickup Time</label>
            <input
              type="time"
              name="pickupTime"
              id="pickupTime"
              value={formData.pickupTime}
              onChange={handleChange}
              className={inputClass}
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="contactName" className={labelClass}>Contact Name</label>
            <input
              type="text"
              name="contactName"
              id="contactName"
              value={formData.contactName}
              onChange={handleChange}
              className={inputClass}
              required
            />
          </div>
          <div>
            <label htmlFor="contactPhone" className={labelClass}>Contact Phone</label>
            <input
              type="tel"
              name="contactPhone"
              id="contactPhone"
              value={formData.contactPhone}
              onChange={handleChange}
              className={inputClass}
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="specialInstructions" className={labelClass}>Special Instructions</label>
          <textarea
            name="specialInstructions"
            id="specialInstructions"
            rows="4"
            value={formData.specialInstructions}
            onChange={handleChange}
            className={inputClass}
            placeholder="Any special instructions for the pickup?"
          />
        </div>

        <div>
          <button 
            type="submit" 
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Schedule Pickup
          </button>
        </div>
      </form>
    </div>
  );
}

export default Pickup;
