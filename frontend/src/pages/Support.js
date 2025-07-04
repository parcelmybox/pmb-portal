import React, { useState } from 'react';

function Support() {
  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    attachment: null,
  });

  const [statusMsg, setStatusMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files ? files[0] : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    setErrorMsg('');

    const token = localStorage.getItem('accessToken'); // ✅ Fix: get token

    const data = new FormData();
    data.append('subject', formData.subject);
    data.append('message', formData.message);
    if (formData.attachment) {
      data.append('attachment', formData.attachment);
    }

    try {
      const response = await fetch('http://localhost:8000/api/support-requests/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`, // ✅ Correct token header
          // Don't set Content-Type when using FormData
        },
        body: data,
      });

      if (response.ok) {
        setStatusMsg('Support request submitted successfully!');
        setFormData({ subject: '', message: '', attachment: null });
      } else {
        const error = await response.json();
        setErrorMsg(error.detail || 'Failed to submit support request.');
      }
    } catch (err) {
      setErrorMsg('Something went wrong. Please try again.');
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Customer Support</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Contact Cards */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Contact Us</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <div>
                <h3 className="font-medium text-gray-800">Email Support</h3>
                <p className="text-gray-600">parcelmybox3@gmail.com</p>
                <p className="text-sm text-gray-500">Response time: 12-24 hours</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
              </svg>
              <div>
                <h3 className="font-medium text-gray-800">Live Chat</h3>
                <p className="text-gray-600">Available 24/7</p>
                <p className="text-sm text-gray-500">Instant response</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <div>
                <h3 className="font-medium text-gray-800">Phone Support</h3>
                <p className="text-gray-600">(555) 123-4567</p>
                <p className="text-sm text-gray-500">Mon-Fri 9AM-5PM PST</p>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">FAQ</h2>
          <div className="space-y-4">
            <div className="border-b pb-4">
              <h3 className="font-medium text-gray-800 mb-2">How do I track my package?</h3>
              <p className="text-gray-600">Log in to your account and visit the tracking page.</p>
            </div>
            <div className="border-b pb-4">
              <h3 className="font-medium text-gray-800 mb-2">What are your shipping rates?</h3>
              <p className="text-gray-600">Visit our pricing page for detailed info.</p>
            </div>
            <div className="border-b pb-4">
              <h3 className="font-medium text-gray-800 mb-2">Can I change my delivery address?</h3>
              <p className="text-gray-600">Yes, before the package is shipped.</p>
            </div>
            <div>
              <h3 className="font-medium text-gray-800 mb-2">What if my package is delayed?</h3>
              <p className="text-gray-600">Contact our support team directly.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Support Form */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Submit a Support Request</h2>

        {statusMsg && <p className="text-green-600 mb-4">{statusMsg}</p>}
        {errorMsg && <p className="text-red-600 mb-4">{errorMsg}</p>}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Subject</label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Message</label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows={4}
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              ></textarea>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Upload attachment</label>
              <input
                type="file"
                name="attachment"
                onChange={handleChange}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700"
            >
              Submit Request
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Support;
