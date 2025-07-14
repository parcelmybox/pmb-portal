import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import CourierPlanCard from '../components/CourierPlanCard';


function QuoteResult() {
	const location = useLocation();
	const navigate = useNavigate();
	const { state } = location;

	const [combinedPlans, setCombinedPlans] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState('');

	useEffect(() => {
		if (!state) return;

		const fetchAndCombinePlans = async () => {
			try {
				const response = await fetch('http://localhost:8000/shipping/courier-plans');
				const plans = await response.json();

				const { formData, quoteData } = state;

				const combined = quoteData.prices.map(price => {
					const matchingPlan = plans.find(
						p => p.name.toLowerCase() === price.courier_name.toLowerCase()
					);

					const fallback = {
						name: price.courier_name,
						tagline: 'No tagline available',
						features: [],
						cta: 'Choose',
						isHighlighted: false,
					};

					const finalPlan = matchingPlan || fallback;

					const displayPrice = `₹${Math.ceil(price.fixed_price || price.per_kg_price).toLocaleString()}`
						+ (price.fixed_price == null ? '/kg' : '');

					return {
						...finalPlan,
                        isHighlighted: false,
						priceDisplay: displayPrice,
						priceDetail: `${quoteData.chargeableWeight} ${formData.weightUnit} - ${quoteData.shippingTime} delivery`,
					};
				});

				setCombinedPlans(combined);
			} catch (err) {
				console.error(err);
				setError('Failed to load courier plans.');
			} finally {
				setLoading(false);
			}
		};

		fetchAndCombinePlans();
	}, [state]);

	if (!state) {
		return (
			<p>
				No quote data found. 
                <button
                    onClick={() => navigate('/')}
                    className="flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-4"
                >
                    Go back
                </button>
			</p>
		);
	}

	// Normal render
	const { formData } = state;

	return (
		<div className="max-w-4xl mx-auto p-6">
			<h1 className="text-3xl font-bold mb-4">Shipping Quote Results</h1>

			{loading && <p>Loading plans...</p>}
			{error && <p className="text-red-600">{error}</p>}

			{!loading && !error && combinedPlans.length > 0 && (
				<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
					{combinedPlans.map((plan, i) => (
						<CourierPlanCard key={i} plan={plan} />
					))}
				</div>
			)}
		</div>
	);
}

export default QuoteResult;
