import React from 'react';

function CourierPlanCard({ plan, setCarrierPreference }) {
  return (
    <div
      className={`rounded-lg shadow-lg overflow-hidden border-2 flex flex-col justify-between ${
        plan.isHighlighted ? 'border-orange-500' : 'border-gray-200'
      } bg-white`}
    >
      <div className={`p-6 ${plan.isHighlighted ? 'bg-orange-500 text-white' : 'bg-green-100 text-gray-800'}`}>
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

        <button
          className={`mt-6 w-full py-2 rounded font-semibold text-sm ${
            plan.isHighlighted
              ? 'bg-white text-orange-500 border border-orange-500 hover:bg-orange-100'
              : 'bg-green-500 text-white hover:bg-green-600'
          }`}
          onClick={setCarrierPreference && (() => setCarrierPreference(plan.name))}
        >
          {plan.cta}
        </button>
      </div>
    </div>
  );
}

export default CourierPlanCard;
