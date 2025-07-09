import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Quote() {
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
		usdRate: 82.5, // Approximate USD to INR rate
		weightUnit: 'kg',
		carrierPreferenceType: 'fastest',
		carrierPreference: '',
	});

	const [quote, setQuote] = useState({
		prices: [],
		shippingTime: '',
		loading: false,
		error: '',
		chargeableWeight: 0,
		volumetric_used: false,
	});

	const [usdRate, setUsdRate] = useState(82.5);

	const checkAllRequiredFields = () => {
		const { originCity, destinationCity, weight, includeDimensions, length, height, width } = formData;
		if (originCity === '' || destinationCity === '' || weight === '') return false;
		else if (includeDimensions === true && (length == 0 || width == 0 || height == 0)) return false;
		return true;
	}

	const calculateQuote = async () => {
		try {
			setQuote(prev => ({ ...prev, loading: true, error: [] }));
			if (checkAllRequiredFields()) {
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
					})
				})
					.then((response) => {
						if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
						return response.json();
					})
					.then((data) => {
						if (data.chargeable_weight > 70) {
							setQuote({
								prices: [],
								shippingTime: '',
								chargeableWeight: 0,
								volumetric_used: false,
								loading: false,
								error: 'Weight exceeds 70 kg limit'
							});
						} else {
							setQuote({
								prices: data.prices,
								shippingTime: data.shipping_time,
								chargeableWeight: data.chargeable_weight,
								volumetric_used: data.volumetric_used,
								loading: false,
								error: ''
							});
						}
					});
			} else {
				setQuote({
					prices: [],
					shippingTime: '',
					chargeableWeight: 0,
					volumetric_used: false,
					loading: false,
					error: 'Fill all relevant details'
				});
			}

		} catch (error) {
			setQuote({
				prices: [],
				shippingTime: '',
				chargeableWeight: 0,
				volumetric_used: false,
				loading: false,
				error: 'Error calculating quote. Please try again.'
			});
		}
	};

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

	const handleSubmit = (e) => {
		e.preventDefault();
		calculateQuote();
		console.log('Form Data Submitted:', formData);
		alert('Quote request submitted! Check console for data. Calculation logic coming soon.');
	};

	const formatPrice = (prices, currency) => {
		if (currency == '₹') {
			return `${Math.ceil(prices.fixed_price === null ? (prices.per_kg_price) : (prices.fixed_price)).toLocaleString()}${(prices.fixed_price === null) ? "/kg" : ''}`;
		} else {
			return `${Math.ceil(prices.fixed_price === null ? (prices.per_kg_price / formData.usdRate) : (prices.fixed_price / formData.usdRate)).toLocaleString()}${prices.fixed_price === null ? "/kg" : ''}`;
		}
	}

	useEffect(() => {
		console.log(formData);
	}, [formData]);

	const inputClass = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
	const labelClass = "block text-sm font-medium text-gray-700";

	return (
		<div className="max-w-2xl mx-auto p-4">
			<div className="space-y-6">
				<h1 className="text-2xl font-bold text-gray-900 mb-6">Request a Shipping Quote</h1>
				<p className="text-gray-600 mb-6">
					Get instant shipping quotes in both INR and USD. Prices include all handling and customs fees.
				</p>
				<form onSubmit={handleSubmit} className="space-y-6">
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

					<div>
						<label htmlFor="originCity" className={labelClass}>Origin City</label>
						<select name="originCity" id="originCity" value={formData.originCity} onChange={handleChange} className={inputClass} required>
							<option value="">Select origin city</option>
							{formData.shippingRoute === 'india-to-usa' ? (
								<>
									<option value="mumbai">Mumbai</option>
									<option value="delhi">New Delhi</option>
									<option value="bangalore">Bangalore</option>
									<option value="chennai">Chennai</option>
									<option value="hyderabad">Hyderabad</option>
								</>
							) : (
								<>
									<option value="new-york">New York</option>
									<option value="los-angeles">Los Angeles</option>
									<option value="chicago">Chicago</option>
									<option value="houston">Houston</option>
									<option value="atlanta">Atlanta</option>
								</>
							)}
						</select>
					</div>
					<div>
						<label htmlFor="destinationCity" className={labelClass}>Destination City</label>
						<select name="destinationCity" id="destinationCity" value={formData.destinationCity} onChange={handleChange} className={inputClass} required>
							<option value="">Select destination city</option>
							{formData.shippingRoute === 'india-to-usa' ? (
								<>
									<option value="new-york">New York</option>
									<option value="los-angeles">Los Angeles</option>
									<option value="chicago">Chicago</option>
									<option value="houston">Houston</option>
									<option value="atlanta">Atlanta</option>
								</>
							) : (
								<>
									<option value="mumbai">Mumbai</option>
									<option value="delhi">New Delhi</option>
									<option value="bangalore">Bangalore</option>
									<option value="chennai">Chennai</option>
									<option value="hyderabad">Hyderabad</option>
								</>
							)}
						</select>
					</div>

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

					{/* <h2 className="text-lg font-medium text-gray-900 pt-4">Carrier Preference</h2>
					<div className="flex items-center space-x-4">
						<input type="radio" id="fastest" name="carrierPreferenceType" value="fastest"
							checked={formData.carrierPreferenceType === "fastest"}
							onChange={(e) => setFormData({ ...formData, carrierPreferenceType: e.target.value })}
							className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
						<label htmlFor="fastest" className="text-sm font-medium text-gray-700">Fastest</label>

						<input type="radio" id="cheapest" name="carrierPreferenceType" value="cheapest"
							checked={formData.carrierPreferenceType === "cheapest"}
							onChange={(e) => setFormData({ ...formData, carrierPreferenceType: e.target.value })}
							className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
						<label htmlFor="cheapest" className="text-sm font-medium text-gray-700">Cheapest</label>

						<input type="radio" id="choose-manually" name="carrierPreferenceType" value="choose-manually"
							checked={formData.carrierPreferenceType === "choose-manually"}
							onChange={(e) => setFormData({ ...formData, carrierPreferenceType: e.target.value })}
							className="h-4 w-4 text-indigo-600 focus:ring-indigo-500" />
						<label htmlFor="choose-manually" className="text-sm font-medium text-gray-700">Choose Manually</label>
					</div> */}

					{formData.carrierPreferenceType === 'choose-manually' && (
						<div>
							<label htmlFor="carrierPreference" className={labelClass}>Select Carrier</label>
							<select name="carrierPreference" id="carrierPreference" value={formData.carrierPreference} onChange={handleChange} className={inputClass}>
								<option value="">Choose carrier</option>
								<option value="ups">UPS</option>
								<option value="dhl">DHL</option>
								<option value="fedex">FedEx</option>
							</select>
						</div>
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

				{(quote.prices.length != 0 && quote.error === '' && quote.shippingTime !== '') && (
					<div className="mt-8 bg-white rounded-lg shadow-lg p-6">
						<h2 className="text-xl font-semibold text-gray-800 mb-4">Your Quote</h2>
						<div className="space-y-4">
							<div className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-2 md:space-y-0 md:space-x-4">
								<div className="flex-1">
									<span className="text-gray-600">Route</span>
									<br />
									<span className="text-indigo-600 font-semibold text-lg">
										{formData.shippingRoute === 'india-to-usa' ? 'India to USA' : 'USA to India'}
									</span>
								</div>
								<div className="flex-1 text-left md:text-right">
									<span className="text-gray-600">Chargeable Weight</span>
									<br />
									<span className="text-indigo-600 font-semibold text-lg">
										{quote.chargeableWeight} {formData.weightUnit}
									</span>
								</div>
							</div>
							<div className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-2 md:space-y-0 md:space-x-4">
								<div className="flex-1">
									<span className="text-gray-600">Package Type</span>
									<br />
									<span className="text-indigo-600 font-semibold text-lg">
										{formData.packageType.charAt(0).toUpperCase() + formData.packageType.slice(1)}
									</span>
								</div>
								<div className="flex-1 text-left md:text-right">
									<span className="text-gray-600">Price in INR</span>
									<br />
									<span className="text-black-600 mr-1">{`${quote.prices[0].courier_name}`}&nbsp;</span>
									<span className="text-indigo-600 font-semibold">
										₹{formatPrice(quote.prices[0], '₹')}
									</span><br />
									{formData.packageType === "package" && (
										<>
											<span className="text-black-600 mr-1">{`${quote.prices[1].courier_name || ''}`}&nbsp;</span>
											<span className="text-indigo-600 font-semibold">
												₹{formatPrice(quote.prices[1] || 0, '₹')}
											</span><br />
											<span className="text-black-600 mr-1">{`${quote.prices[2].courier_name || ''}`}&nbsp;</span>
											<span className="text-indigo-600 font-semibold">
												₹{formatPrice(quote.prices[2] || 0, '₹')}
											</span><br />
										</>
									)}
								</div>
							</div>
							<div className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-2 md:space-y-0 md:space-x-4">
								<div>
									<span className="text-gray-600">Price in USD</span>
									<br />
									<span className="text-black-600 mr-1">{`${quote.prices[0].courier_name}`}</span>
									<span className="text-indigo-600 font-semibold">
										${formatPrice(quote.prices[0], '$')}
									</span><br />
									{formData.packageType === "package" && (
										<>
											<span className="text-black-600 mr-1">{`${quote.prices[1].courier_name}`}</span>
											<span className="text-indigo-600 font-semibold">
												${formatPrice(quote.prices[1], '$')}
											</span><br />
											<span className="text-black-600 mr-1">{`${quote.prices[2].courier_name}`}</span>
											<span className="text-indigo-600 font-semibold">
												${formatPrice(quote.prices[2], '$')}
											</span><br />
										</>
									)}
								</div>
								<div className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-2 md:space-y-0 md:space-x-4">
									<div className="flex-1">
										<span className="text-gray-600">Current Exchange Rate</span>
										<br />
										<span className="text-indigo-600 font-semibold text-lg">1 USD = {usdRate} INR</span>
									</div>
								</div>
							</div>
						</div>

						<div className="mt-6">
							{quote.volumetric_used && (
								<div className="flex text-sm">
									<p className="text-gray-600 text-gray-600">
										* Volumetric Weight is being used for pricing. &nbsp;
									</p>
									<a href='https://www.parcelhero.com/en-gb/support/volumetric-weight-calculator'>
										<span className="text-indigo-600 semibold">What is Volumetric Weight?</span>
									</a>
								</div>
							)}
							<div className="mt-1">
								<p className="text-sm text-gray-600">
									** Prices include all handling and customs fees. Delivery times and estimates may vary.
								</p>
							</div>
						</div>
					</div>
				)}

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
