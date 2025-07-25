import React, { useState } from 'react';
import { StarIcon } from '@heroicons/react/24/solid';

function Feedback() {
  const [formData, setFormData] = useState({
    orderId: '',
    message: '',
    image: null,
    rating: 0,
  });

  const [imagePreview, setImagePreview] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (files) {
      setFormData((prev) => ({
        ...prev,
        [name]: files[0],
      }));
      setImagePreview(URL.createObjectURL(files[0]));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleRating = (star) => {
    setFormData((prev) => ({
      ...prev,
      rating: star,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Feedback submitted:', formData); // ← This contains rating too
    setSuccess(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-blue-100 to-purple-100 flex items-center justify-center px-4 py-8 overflow-hidden">
      <div className="w-full max-w-xl bg-white shadow-2xl rounded-2xl p-8">
        <h2 className="text-3xl font-extrabold text-center text-blue-800 mb-6">
          Customer Feedback
        </h2>

        {success ? (
          <div className="text-green-600 font-semibold text-center text-lg">
            ✅ Thank you for your feedback!
          </div>
        ) : (
          <>
            {/* Star Rating */}
            <div className="text-center mb-8">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Rate Our Service
              </label>
              <div className="flex justify-center space-x-3">
                {[1, 2, 3, 4, 5].map((star) => (
                  <StarIcon
                    key={star}
                    className={`h-10 w-10 cursor-pointer transition duration-200 ${
                      formData.rating >= star ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                    onClick={() => handleRating(star)}
                  />
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Order ID Dropdown */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Related Order
                </label>
                <select
                  name="orderId"
                  required
                  value={formData.orderId}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800"
                >
                  <option value="">Select your order</option>
                  <option value="PMB23523">PMB23523</option>
                  <option value="PMB87912">PMB87912</option>
                  <option value="PMB44156">PMB44156</option>
                </select>
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Message
                </label>
                <textarea
                  name="message"
                  rows="3"
                  required
                  value={formData.message}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 text-gray-800 resize-none"
                  placeholder="Write your feedback here..."
                ></textarea>
              </div>

              {/* Image Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Attach Image (optional)
                </label>
                <input
                  type="file"
                  name="image"
                  accept="image/*"
                  onChange={handleChange}
                  className="block w-full text-sm text-gray-600"
                />
                {imagePreview && (
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="mt-3 rounded-lg shadow-md max-h-48 object-contain"
                  />
                )}
              </div>

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  className="w-full py-3 px-6 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold text-lg rounded-md shadow-lg transition"
                >
                  Submit Feedback
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

export default Feedback;
