import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Quote() {
  const [formData, setFormData] = useState({
    shippingRoute: 'india-to-usa',
    originCity: '',
    destinationCity: '',
    weight: '',
    length: '',
    width: '',
    height: '',
    packageType: 'document',
    currency: '₹',
    usdRate: 82.5, // Approximate USD to INR rate
    weightUnit: 'kg',
  });

  const [quote, setQuote] = useState({
    inrPrice: 0,
    usdPrice: 0,
    shippingTime: '',
    loading: false,
    error: ''
  });

  const calculateQuote = async () => {
    try {
      setQuote(prev => ({ ...prev, loading: true, error: '' }));
      
      // fetching calculated data from api
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      fetch(`${API_URL}/api/quote/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          shipping_route: formData.shippingRoute,
          type: formData.packageType,
          weight: formData.weight,
          weight_metric: formData.weightUnit,
          dim_length: formData.length,
          dim_width: formData.width,
          dim_height: formData.height,
          origin: formData.originCity,
          destination: formData.destinationCity,
        })
      })
        .then((response) => {
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          return response.json();
        })
        .then((data) => {
          setQuote({
            inrPrice: data.inr_price,
            usdPrice: data.usd_price,
            shippingTime: data.shipping_time,
            loading: false,
            error: ''
          });
        });
        // .catch((err) => {
        //   setQuote(prevState => ({
        //     ...prevState,
        //     error: 
        //   }))
        // })

    } catch (error) {
      setQuote({
        inrPrice: 0,
        usdPrice: 0,
        shippingTime: '',
        loading: false,
        error: 'Error calculating quote. Please try again.'
      });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    calculateQuote();
    console.log('Form Data Submitted:', formData);
    alert('Quote request submitted! Check console for data. Calculation logic coming soon.');
  };

  const inputClass = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
  const labelClass = "block text-sm font-medium text-gray-700";

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Request a Shipping Quote</h1>
        <p className="text-gray-600 mb-6">
          Get instant shipping quotes in both INR and USD. Prices include all handling and customs fees.
        </p>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <input type="radio" id="india-to-usa" name="shippingRoute" value="india-to-usa" 
                     checked={formData.shippingRoute === 'india-to-usa'}
                     onChange={(e) => setFormData({...formData, shippingRoute: e.target.value})}
                     className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
              <label htmlFor="india-to-usa" className="text-sm font-medium text-gray-700">India to USA</label>

              <input type="radio" id="usa-to-india" name="shippingRoute" value="usa-to-india"
                     checked={formData.shippingRoute === 'usa-to-india'}
                     onChange={(e) => setFormData({...formData, shippingRoute: e.target.value})}
                     className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
              <label htmlFor="usa-to-india" className="text-sm font-medium text-gray-700">USA to India</label>
            </div>

            <div>
              <label htmlFor="packageType" className={labelClass}>Package Type</label>
              <select name="packageType" id="packageType" value={formData.packageType} onChange={handleChange} className={inputClass} required>
                <option value="document">Document</option>
                <option value="package">Package</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="originCity" className={labelClass}>Origin City</label>
            <select name="originCity" id="originCity" value={formData.originCity} onChange={handleChange} className={inputClass} required>
              <option value="">Select origin city</option>
              {formData.shippingRoute === 'india-to-usa' ? (
                <>
                  <option value="mumbai">Mumbai</option>
                  <option value="delhi">New Delhi</option>
                  <option value="bangalore">Bangalore</option>
                  <option value="chennai">Chennai</option>
                  <option value="hyderabad">Hyderabad</option>
                </>
              ) : (
                <>
                  <option value="new-york">New York</option>
                  <option value="los-angeles">Los Angeles</option>
                  <option value="chicago">Chicago</option>
                  <option value="houston">Houston</option>
                  <option value="atlanta">Atlanta</option>
                </>
              )}
            </select>
          </div>
          <div>
            <label htmlFor="destinationCity" className={labelClass}>Destination City</label>
            <select name="destinationCity" id="destinationCity" value={formData.destinationCity} onChange={handleChange} className={inputClass} required>
              <option value="">Select destination city</option>
              {formData.shippingRoute === 'india-to-usa' ? (
                <>
                  <option value="new-york">New York</option>
                  <option value="los-angeles">Los Angeles</option>
                  <option value="chicago">Chicago</option>
                  <option value="houston">Houston</option>
                  <option value="atlanta">Atlanta</option>
                </>
              ) : (
                <>
                  <option value="mumbai">Mumbai</option>
                  <option value="delhi">New Delhi</option>
                  <option value="bangalore">Bangalore</option>
                  <option value="chennai">Chennai</option>
                  <option value="hyderabad">Hyderabad</option>
                </>
              )}
            </select>
          </div>

          <div>
            <label htmlFor="weight" className={labelClass}>Package Weight</label>
            <div className="flex space-x-2">
              <input type="number" name="weight" id="weight" value={formData.weight} onChange={handleChange} 
                     className={inputClass} required min="0.1" step="0.1" />
              <select name="weightUnit" id="weightUnit" value={formData.shippingRoute === 'india-to-usa' ? 'kg' : 'lbs'} 
                      onChange={(e) => setFormData({...formData, weightUnit: e.target.value})} 
                      className={inputClass}>
                <option value="kg">kg</option>
                <option value="lbs">lbs</option>
              </select>
            </div>
          </div>

          <h2 className="text-lg font-medium text-gray-900 pt-4">Package Dimensions (inches)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="length" className={labelClass}>Length</label>
              <input type="number" name="length" id="length" value={formData.length} onChange={handleChange} 
                     className={inputClass} required min="0" step="0.1" />
            </div>
            <div>
              <label htmlFor="width" className={labelClass}>Width</label>
              <input type="number" name="width" id="width" value={formData.width} onChange={handleChange} 
                     className={inputClass} required min="0" step="0.1" />
            </div>
            <div>
              <label htmlFor="height" className={labelClass}>Height</label>
              <input type="number" name="height" id="height" value={formData.height} onChange={handleChange} 
                     className={inputClass} required min="0" step="0.1" />
            </div>
          </div>

          <div>
            <button 
              type="button" 
              onClick={calculateQuote}
              disabled={quote.loading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                quote.loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {quote.loading ? 'Calculating...' : 'Get Quote'}
            </button>
          </div>
        </form>

        {(quote.inrPrice > 0 && quote.usdPrice > 0 && quote.error === '' && quote.shippingTime !== '') && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Your Quote</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <span className="text-gray-600">Route</span>
                  <br />
                  <span className="text-indigo-600 font-semibold text-lg">
                    {formData.shippingRoute === 'india-to-usa' ? 'India to USA' : 'USA to India'}
                  </span>
                </div>
                <div className="flex-1 text-right">
                  <span className="text-gray-600">Weight</span>
                  <br />
                  <span className="text-indigo-600 font-semibold text-lg">
                    {formData.weight} {formData.shippingRoute === 'india-to-usa' ? 'kg' : 'lbs'}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <span className="text-gray-600">Package Type</span>
                  <br />
                  <span className="text-indigo-600 font-semibold text-lg">
                    {formData.packageType === 'document' ? 'Document' : 'Package'}
                  </span>
                </div>
                <div className="flex-1 text-right">
                  <span className="text-gray-600">Price in INR</span>
                  <br />
                  <span className="text-2xl font-bold text-indigo-600">₹{quote.inrPrice.toLocaleString()}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <span className="text-gray-600">Price in USDa</span>
                  <br />
                  <span className="text-2xl font-bold text-indigo-600">${quote.usdPrice.toLocaleString()}</span>
                </div>
                <div className="flex-1 text-right">
                  <span className="text-gray-600">Estimated Delivery</span>
                  <br />
                  <span className="text-indigo-600 font-semibold text-lg">{quote.shippingTime}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <span className="text-gray-600">Current Exchange Rate</span>
                  <br />
                  <span className="text-indigo-600 font-semibold text-lg">1 USD = {formData.usdRate} INR</span>
                </div>
              </div>
            </div>
            <div className="mt-6">
              <p className="text-sm text-gray-600">
                * Prices include all handling and customs fees. Delivery times and estimates may vary.
              </p>
            </div>
          </div>
        )}

        {quote.error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">
            {quote.error}
          </div>
        )}
      </div>
    </div>
  );
}

export default Quote;
