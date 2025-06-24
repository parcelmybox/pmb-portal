import React, { useEffect, useState } from 'react';
import CourierPlanCard from '../components/CourierPlanCard';

function Pricing() {
  const [courierPlans, setCourierPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); console.log("API URL:", process.env.REACT_APP_API_URL);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/shipping/courier-plans/`)
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setCourierPlans(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-center mt-10">Loading shipping options...</p>;
  if (error) return <p className="text-center mt-10 text-red-600">Error: {error}</p>;

  return (
    <div className="bg-white min-h-screen p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-8 text-center text-gray-800">Choose Your Shipping Option</h1>
      <div className="grid md:grid-cols-3 gap-6 w-full max-w-6xl">
        {courierPlans.map((plan, index) => (
          <CourierPlanCard key={index} plan={plan} />
        ))}
      </div>
    </div>
  );
}

export default Pricing;
