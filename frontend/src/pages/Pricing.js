import React from 'react';

const courierPlans = [
  {
    name: 'UPS Shipping',
    tagline: 'Reliable & Progressive Value',
    priceDisplay: '₹2800+',
    priceDetail: '740/kg',
    isHighlighted: true,
    features: [
      'Best for standard international shipping',
      'Basic tracking included',
      'Insurance available separately',
      'Support for bulk consolidation',
    ],
    cta: 'Ship with UPS'
  },
  {
    name: 'DHL Shipping',
    tagline: 'Fast & Premium Delivery',
    priceDisplay: '₹3600+',
    priceDetail: '₹780/kg for above 5kgs',
    isHighlighted: false,
    features: [
      '3–5 Day delivery',
      'Includes advanced tracking',
      'Priority handling',
      'Reliable courier partner',
    ],
    cta: 'Ship with DHL'
  },
  {
    name: 'FedEx Shipping',
    tagline: 'Affordable & Consistent',
    priceDisplay: '₹2700+',
    priceDetail: '₹730/kg above 10 kg',
    isHighlighted: false,
    features: [
      '5–7 Day delivery',
      'Tracking included',
      'Good for light to medium parcels',
      'Trusted international service',
    ],
    cta: 'Ship with FedEx'
  }
];

function Pricing() {
  return (
    <div className="bg-white min-h-screen p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-8 text-center text-gray-800">Choose Your Shipping Option</h1>
      <div className="grid md:grid-cols-3 gap-6 w-full max-w-6xl">
        {courierPlans.map((plan, index) => (
          <div
            key={index}
            className={rounded-lg shadow-lg overflow-hidden border-2 flex flex-col justify-between ${
              plan.isHighlighted ? 'border-orange-500' : 'border-gray-200'
            } bg-white}
          >
            <div className={p-6 ${plan.isHighlighted ? 'bg-orange-500 text-white' : 'bg-green-100 text-gray-800'}}>
              <h2 className="text-xl font-bold">{plan.name}</h2>
              <p className="text-sm mt-1">{plan.tagline}</p>
            </div>

            <div className="p-6 text-center">
              <p className="text-2xl font-bold text-blue-600">{plan.priceDisplay}</p>
              <p className="text-gray-600 text-sm mt-1">{plan.priceDetail}</p>

              <ul className="mt-4 space-y-2 text-left text-sm text-gray-700">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start">
                    <span className="text-green-500 mr-2">✔</span>
                    {feature}
                  </li>
                ))}
              </ul>

              <button className={mt-6 w-full py-2 rounded font-semibold text-sm ${
                plan.isHighlighted ? 'bg-white text-orange-500 border border-orange-500' : 'bg-green-500 text-white hover:bg-green-600'
              }}>
                {plan.cta}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Pricing;
