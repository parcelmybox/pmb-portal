import React from 'react';
import { Link } from 'react-router-dom';

function Dashboard() {
  const cardClass = "bg-white shadow-lg rounded-lg p-6 hover:shadow-xl transition-shadow duration-300 ease-in-out";
  const linkClass = "text-blue-600 hover:text-blue-800 font-semibold";

  const features = [
    {
      title: "Swift Deliveries, Global Reach",
      desc: "Delivering parcels to the USA with speed and efficiency. Connecting you to the world seamlessly.",
      icon: "🚚",
      bg: "bg-blue-50"
    },
    {
      title: "Secure and Trusted",
      desc: "Your packages are in safe hands. Parcel My Box provides a secure and reliable international courier service for the safe delivery of your shipments.",
      icon: "🔒",
      bg: "bg-blue-100"
    },
    {
      title: "Affordable and Transparent",
      desc: "Enjoy cost-effective shipping solutions without compromising on service quality. Transparent pricing ensures clarity with no hidden fees.",
      icon: "💰",
      bg: "bg-blue-50"
    },
    {
      title: "Personalized Service",
      desc: "Understanding your unique shipping needs. Providing personalized courier solutions designed to cater to your specific requirements.",
      icon: "🧑‍💼",
      bg: "bg-blue-100"
    },
    {
      title: "Customer Satisfaction Guaranteed",
      desc: "Parcel My Box is committed to customer satisfaction. Dedicated to providing excellent customer service for a smooth and enjoyable shipping experience.",
      icon: "📦",
      bg: "bg-blue-50"
    },
    {
      title: "Reliability and Convenience",
      desc: "Choose reliability as a hallmark of Parcel My Box services. Opt for convenience in international shipping with a trusted partner.",
      icon: "✅",
      bg: "bg-blue-100"
    }
  ];

  const locations = [
    "USA – Raleigh",
    "USA – Bay Area",
    "Hyderabad",
    "Chennai",
    "Bangalore"
  ];

  return (
    <div className="p-6 space-y-12">
     
      <h1 className="text-3xl font-bold text-gray-900 mb-4"></h1>
 
      

      {/* Why Choose Us */}
      <div>
        <h2 className="text-3xl font-bold text-blue-800 text-center mb-2">Why Choose Parcel My Box</h2>
        <p className="text-gray-600 text-center mb-10 max-w-3xl mx-auto">
          Your Gateway to Effortless Global Shipping. Choose reliability, choose convenience, choose us for international courier services from India to USA.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`${feature.bg} rounded-lg p-6 shadow transition duration-300 hover:bg-blue-200 hover:text-blue-900`}
            >
              <div className="text-3xl mb-3 text-blue-600">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-blue-800 mb-2">{feature.title}</h3>
              <p className="text-gray-700">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Operating Locations */}
      <div>
        <h2 className="text-3xl font-bold text-blue-800 text-center mb-2">Areas of Service</h2>
        <p className="text-gray-600 text-center mb-8 max-w-3xl mx-auto">
          Parcel My Box extends its services across the globe, with a focus on seamless deliveries to the USA. Trust us for international courier excellence, wherever your parcels need to reach.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          {locations.map((loc, idx) => (
            <div
              key={idx}
              className="bg-blue-50 text-blue-800 px-5 py-2 rounded-full shadow hover:bg-blue-200 hover:text-blue-900 transition duration-300"
            >
              {loc}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-20 border-t pt-10">
        <p className="text-center text-lg font-medium text-blue-800 mb-8">
          Your Gateway to Effortless Global Shipping. Choose reliability, choose convenience, choose us for international courier services from India to USA.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-gray-700 text-sm px-4 md:px-0 max-w-6xl mx-auto">
          {/* Column 1: Address & Email */}
          <div>
            <h4 className="text-blue-800 font-semibold mb-2">Warehouse Address</h4>
            <p>Pachavati Apartments</p>
            <p>Pragathi Nagar</p>
            <p>Hyderabad 500090</p>

            <h4 className="text-blue-800 font-semibold mt-4 mb-2">Email</h4>
            <a href="mailto:parcelmybox3@gmail.com" className="text-blue-600 hover:underline">
              parcelmybox3@gmail.com
            </a>
          </div>

          {/* Column 2: Phone */}
          <div>
            <h4 className="text-blue-800 font-semibold mb-2">Talk to Us</h4>
            <p>001-510 714 6946</p>
            <p>+91 92474 99247</p>
            <p>+91 92966 02230</p>
          </div>

          {/* Column 3: Help & Social */}
          <div>
            <h4 className="text-blue-800 font-semibold mb-2">Help</h4>
            <a href="#" className="block text-blue-600 hover:underline">Pickup Request</a>

            <h4 className="text-blue-800 font-semibold mt-4 mb-2">Follow Us</h4>
            <div className="flex space-x-4">
              <a href="#" className="text-blue-600 hover:text-blue-800">Facebook</a>
              <a href="#" className="text-blue-600 hover:text-blue-800">Instagram</a>
            </div>
          </div>
        </div>

        <p className="text-center text-gray-500 mt-10 text-xs">&copy; {new Date().getFullYear()} Parcel My Box. All rights reserved.</p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className={cardClass}>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Get a Shipping Quote</h2>
          <p className="text-gray-600 mb-4">
            Get an estimate for shipping between India and USA. Choose from standard or priority shipping options.
          </p>
          <Link to="/quote" className={linkClass}>Request a Quote &rarr;</Link>
        </div>

        <div className={cardClass}>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Track Your International Shipment</h2>
          <p className="text-gray-600 mb-4">
            Track your international shipments between India and USA. Get real-time updates on your parcel's journey.
          </p>
          <Link to="/tracking" className={linkClass}>Track a Parcel &rarr;</Link>
        </div>

        <div className={cardClass}>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Your Profile</h2>
          <p className="text-gray-600 mb-4">
            Manage your account settings and preferences.
          </p>
          <Link to="/profile" className={linkClass}>Go to Profile &rarr;</Link>
        </div>
      </div>

    </div>
  );
}

export default Dashboard;
