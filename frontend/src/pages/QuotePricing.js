import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import CourierPlanCard from '../components/CourierPlanCard';

function QuoteResult() {
	const location = useLocation();
	const navigate = useNavigate();
	const { state } = location;

	const [combinedPlans, setCombinedPlans] = useState([]);
	const [carrierPreference, setCarrierPreference] = useState("UPS Shipping");
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState('');

	const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

	useEffect(() => {
		if (!state) return;

		const fetchAndCombinePlans = async () => {
			try {
				const response = await fetch(`${API_URL}/shipping/courier-plans`);
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

	const downloadPDF = () => {
		const payload = {
			formData: formData,
			quoteData: quoteData,
			carrierPreference: carrierPreference,
		};

		fetch(`${API_URL}/api/generate-quote-pdf/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(payload),
		})
			.then(response => {
				if (!response.ok) {
					throw new Error('Failed to generate invoice');
				}
				return response.blob();
			})
			.then(blob => {
				const url = window.URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.href = url;
				link.setAttribute('download', 'invoice.pdf');
				document.body.appendChild(link);
				link.click();
				link.remove();
			})
			.catch(error => {
				console.error('Error:', error.message);
			});
	};

	// Normal render
	const { formData, quoteData } = state;

	return (
		<div className="max-w-4xl mx-auto p-6">
			<div className='flex justify-between items-center'>
				<h1 className="text-3xl font-bold mb-4">Shipping Quote Results</h1>
				<div className='flex gap-2'>
					<button
						onClick={() => navigate('/quote')}
						className="rounded-md bg-indigo-600 p-2 hover:bg-indigo-700 focus:ring-indigo-700"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							className="h-5 w-5 text-white"
							viewBox="0 0 20 20"
							fill="currentColor"
						>
							<path
								fillRule="evenodd"
								d="M7.707 14.707a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414l5-5a1 1 0 011.414 1.414L4.414 9H17a1 1 0 110 2H4.414l3.293 3.293a1 1 0 010 1.414z"
								clipRule="evenodd"
							/>
						</svg>
					</button>
					<button
						onClick={downloadPDF}
						className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md shadow hover:bg-indigo-700 transition"
					>
						Export PDF
					</button>
				</div>
			</div>

			{loading && <p>Loading plans...</p>}
			{error && <p className="text-red-600">{error}</p>}

			{!loading && !error && combinedPlans.length > 0 && (
				<>
					<p className="my-6 text-lg font-medium">
						Package type: <span className="font-semibold">{formData.packageType.charAt(0).toUpperCase() + formData.packageType.slice(1)}</span>
					</p>

					{quoteData.volumetricUsed === true && (
						<div className="my-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-lg">
							<p className="text-yellow-700 font-medium">
								* Volumetric weight used for pricing calculation
							</p>
						</div>
					)}

					{formData.packageType === "medicine" && (
						<div className="my-4 bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
							<h3 className="font-semibold text-blue-700">Required Documents for Medicine:</h3>
							<ul className="list-disc list-inside text-sm text-gray-700 mt-2">
								<li>Doctor's Prescription</li>
								<li>Purchase Invoice</li>
								<li>Copy of Aadhaar/Passport</li>
							</ul>
						</div>
					)}

					{formData.packageType === "document" && (
						<div className="my-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
							<h3 className="font-semibold text-yellow-700">Required Documents for Document:</h3>
							<p className="text-sm text-gray-700 mt-2">No additional documents required.</p>
						</div>
					)}

					<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
						{combinedPlans.map((plan, i) => (
							<CourierPlanCard
								key={i}
								plan={{
									...plan,
									isHighlighted: plan.name.toLowerCase() === carrierPreference.toLowerCase()
								}}
								setCarrierPreference={setCarrierPreference} />
						))}
					</div>
				</>
			)}
		</div>
	);
}

export default QuoteResult;
