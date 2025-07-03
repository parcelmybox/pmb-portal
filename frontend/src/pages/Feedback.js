import React, { useState } from 'react';

function Feedback() {
  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    image: null,
  });

  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files ? files[0] : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Feedback submitted:', formData);
    setSuccess(true);
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white shadow-md rounded-md mt-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Customer Feedback</h2>
      
      {success ? (
        <div className="text-green-600 font-medium">Thank you for your feedback!</div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Subject</label>
            <input
              type="text"
              name="subject"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2"
              value={formData.subject}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Message</label>
            <textarea
              name="message"
              rows="4"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2"
              value={formData.message}
              onChange={handleChange}
              required
            ></textarea>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Attach Image (optional)</label>
            <input
              type="file"
              name="image"
              accept="image/*"
              className="mt-1 block"
              onChange={handleChange}
            />
          </div>

          <button
            type="submit"
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700"
          >
            Submit Feedback
          </button>
        </form>
      )}
    </div>
  );
}

export default Feedback;
