import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Quote() {
	const navigate = useNavigate();
	const [formData, setFormData] = useState({
		shippingRoute: 'india-to-usa',
		originCity: '',
		destinationCity: '',
		weight: '',
		includeDimensions: false,
		length: 0,
		width: 0,
		height: 0,
		packageType: 'package',
		currency: '₹',
		weightUnit: 'kg',
		carrierPreferenceType: 'fastest',
		carrierPreference: '',
	});

	// quote calculation output
	const [quote, setQuote] = useState({
		prices: [],
		shippingTime: '',
		loading: false,
		error: '',
		chargeableWeight: 0,
		volumetricUsed: false,
	});

	// state variable for fetching USD -> INR conversion rate
	const [usdRate, setUsdRate] = useState(82.5);

	const checkAllRequiredFields = () => {
		const { originCity, destinationCity, weight, includeDimensions, length, height, width } = formData;

		if (!originCity && !destinationCity) return false;

		if (!weight) return false;

		if (includeDimensions && (length <= 0 || width <= 0 || height <= 0)) return false;

		return true;
	}

	const calculateQuote = async () => {
		try {
			setQuote(prev => ({ ...prev, loading: true, error: [] }));
			if (checkAllRequiredFields()) {
				// fetching from quote API endpoint
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
						include_dimensions: formData.includeDimensions,
						dim_length: formData.length,
						dim_width: formData.width,
						dim_height: formData.height,
						origin: formData.originCity,
						destination: formData.destinationCity,
						usd_rate: usdRate,
						carrier_preference_type: formData.carrierPreferenceType,
						carrier_preference: formData.carrierPreference,
						currency: (formData.shippingRoute === 'india-to-usa' ? '₹' : '$'),
					})
				})
					.then((response) => {
						if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
						return response.json();
					})
					.then((data) => {
						// check if volumetric or normal weight exceeds 70 kg weight limit
						if (data.chargeable_weight > 70) {
							setQuote({
								prices: [],
								shippingTime: '',
								chargeableWeight: 0,
								volumetricUsed: false,
								loading: false,
								error: 'Weight exceeds 70 kg limit'
							});
						} else {
							navigate('/quote-result', {
								state: {
									formData: formData,
									quoteData: {
										prices: data.prices,
										shippingTime: data.shipping_time,
										chargeableWeight: data.chargeable_weight,
										volumetricUsed: data.volumetric_used,
										currency: data.currency,
									},
									usdRate: usdRate,
								}
							});
						}
					});
			} else {
				// unfilled mandatory field
				setQuote({
					prices: [],
					shippingTime: '',
					chargeableWeight: 0,
					volumetricUsed: false,
					loading: false,
					error: 'Fill all relevant details'
				});
			}

		} catch (error) {
			setQuote({
				prices: [],
				shippingTime: '',
				chargeableWeight: 0,
				volumetricUsed: false,
				loading: false,
				error: 'Error calculating quote. Please try again.'
			});
		}
	};

	// fetches USD->INR exchange rate from frankfurter API
	useEffect(() => {
		async function fetchExchangeRate() {
			const exchangeRate = await fetch('https://api.frankfurter.app/latest?from=USD&to=INR');
			const response = await exchangeRate.json();
			setUsdRate(response.rates.INR);
		}

		fetchExchangeRate();
	}, []);

	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData(prevState => ({
			...prevState,
			[name]: value
		}));
	};

	// formats prices input to it into locale string, currency symbol and adds '/kg' if required (per kg price)
	const formatPrice = (prices, currency) => {
		if (currency == '₹') {
			return `${Math.ceil(prices.fixed_price === null ? (prices.per_kg_price) : (prices.fixed_price)).toLocaleString()}${(prices.fixed_price === null) ? "/kg" : ''}`;
		} else {
			return `${Math.ceil(prices.fixed_price === null ? (prices.per_kg_price / usdRate) : (prices.fixed_price / usdRate)).toLocaleString()}${prices.fixed_price === null ? "/kg" : ''}`;
		}
	}

	const inputClass = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
	const labelClass = "block text-sm font-medium text-gray-700";

	return (
		<div className="max-w-2xl mx-auto p-4">
			<div className="space-y-6">
				<h1 className="text-2xl font-bold text-gray-900 mb-6">Request a Shipping Quote</h1>
				<p className="text-gray-600 mb-6">
					Get instant shipping quotes in both INR and USD. Prices include all handling and customs fees.
				</p>
				<form onSubmit={calculateQuote} className="space-y-6">
					<div className="space-y-4">
						<div className="flex items-center space-x-4">
							<input type="radio" id="india-to-usa" name="shippingRoute" value="india-to-usa"
								checked={formData.shippingRoute === 'india-to-usa'}
								onChange={(e) => setFormData({ ...formData, shippingRoute: e.target.value })}
								className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
							<label htmlFor="india-to-usa" className="text-sm font-medium text-gray-700">India to USA</label>

							<input type="radio" id="usa-to-india" name="shippingRoute" value="usa-to-india"
								checked={formData.shippingRoute === 'usa-to-india'}
								onChange={(e) => setFormData({ ...formData, shippingRoute: e.target.value })}
								className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
							<label htmlFor="usa-to-india" className="text-sm font-medium text-gray-700">USA to India</label>
						</div>

						<div>
							<label htmlFor="packageType" className={labelClass}>Package Type</label>
							<select name="packageType" id="packageType" value={formData.packageType} onChange={handleChange} className={inputClass} required>
								<option value="package">Package</option>
								<option value="document">Document</option>
								<option value="medicine">Medicine</option>
							</select>
						</div>

						{/* 'documents required' boxes */}
						{formData.packageType === 'medicine' && (
							<div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
								<h3 className="font-semibold text-yellow-700">Required Documents for Medicine:</h3>
								<ul className="list-disc list-inside text-sm text-gray-700 mt-2">
									<li>Doctor's Prescription</li>
									<li>Purchase Invoice</li>
									<li>Copy of Aadhaar/Passport</li>
								</ul>
							</div>
						)}

						{formData.packageType === 'document' && (
							<div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
								<h3 className="font-semibold text-yellow-700">Required Documents for Document:</h3>
								<p className="text-sm text-gray-700 mt-2">No additional documents required.</p>
							</div>
						)}
					</div>

					{formData.shippingRoute === "india-to-usa" && (
						<div>
							<label htmlFor="originCity" className={labelClass}>Origin City</label>
							<select name="originCity" id="originCity" value={formData.originCity} onChange={handleChange} className={inputClass} required>
								<option value="">Select origin city</option>
								<option value="mumbai">Mumbai</option>
								<option value="delhi">New Delhi</option>
								<option value="bangalore">Bangalore</option>
								<option value="chennai">Chennai</option>
								<option value="hyderabad">Hyderabad</option>
							</select>
						</div>
					)}

					{formData.shippingRoute === "usa-to-india" && (
						<div>
							<label htmlFor="destinationCity" className={labelClass}>Destination City</label>
							<select name="destinationCity" id="destintionCity" value={formData.destinationCity} onChange={handleChange} className={inputClass} required>
								<option value="">Select destintion city</option>
								<option value="mumbai">Mumbai</option>
								<option value="delhi">New Delhi</option>
								<option value="bangalore">Bangalore</option>
								<option value="chennai">Chennai</option>
								<option value="hyderabad">Hyderabad</option>
							</select>
						</div>
					)}

					<div>
						<label htmlFor="weight" className={labelClass}>Package Weight</label>
						{formData.packageType === "package" ? (
							<div className="flex space-x-2">
								<input type="number" name="weight" id="weight" value={formData.weight} onChange={handleChange}
									className={inputClass} required min="0.1" step="0.1" />
								<select name="weightUnit" id="weightUnit" value={formData.shippingRoute === 'india-to-usa' ? 'kg' : 'lbs'}
									onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
									className={inputClass}>
									<option value="kg">kg</option>
									<option value="lbs">lbs</option>
								</select>
							</div>)
							: (
								// 2 weight options for document and medicine package types
								<div className="flex items-center space-x-4 mt-4">
									<input type="radio" id="0.5kg" name="weight" value='0.5'
										checked={formData.weight === '0.5'}
										onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
										className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
									<label htmlFor="0.5kg" className="text-sm font-medium text-gray-700">0.5 kg</label>

									<input type="radio" id="1kg" name="weight" value='1'
										checked={formData.weight === '1'}
										onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
										className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
									<label htmlFor="1kg" className="text-sm font-medium text-gray-700">1 kg</label>
								</div>
							)}
					</div>

					{/* option for entering dimensions for volumetric weight calculation (applicable only for packages) */}
					{formData.packageType === 'package' && (
						<div className="flex items-center">
							<input
								id="include-dimensions"
								name="include-dimensions"
								type="checkbox"
								className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
								checked={formData.includeDimensions}
								onChange={() => setFormData((prevState) => ({ ...prevState, includeDimensions: !prevState.includeDimensions }))}
							/>
							<label htmlFor="include-dimensions" className="ml-2 block text-sm text-gray-900">
								Input package dimensions (optional)
							</label>
						</div>
					)}

					{/* dimensions input if above checkbox is checked */}
					{formData.includeDimensions && (
						<>
							<h2 className="text-lg font-medium text-gray-900 pt-4">Package Dimensions (centimetres)</h2>
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
						</>
					)}

					<div>
						<button
							type="button"
							onClick={calculateQuote}
							disabled={quote.loading}
							className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${quote.loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
								}`}
						>
							{quote.loading ? 'Calculating...' : 'Get Quote'}
						</button>
					</div>
				</form>

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
