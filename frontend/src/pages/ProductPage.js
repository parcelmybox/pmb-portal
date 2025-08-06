import React, { useState, useEffect } from "react";
import ImageCarousel from "../components/ImageCarousel";
import BreadCrumbs from "../components/BreadCrumbs";
import { useParams } from 'react-router-dom';
import { toast, Slide } from 'react-toastify';

const ProductPage = () => {
	const [product, setProduct] = useState();
	const [selectedVariant, setSelectedVariant] = useState();
	const [quantity, setQuantity] = useState(1);

	const { productName } = useParams();

	useEffect(() => {
		const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
		fetch(`${API_URL}/api/products/fetch-product/${productName}/`)
			.then((response) => {
				if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
				return response.json();
			})
			.then((data) => {
				setProduct(data);
				if (data.weights.length !== 0) {
					setSelectedVariant(data.weights[0]);
				}
			});
	}, []);

	const onVariantButtonClick = (weight) => {
		const selectedProduct = product.weights.find((product) => product.weights === weight);
		setSelectedVariant(selectedProduct);
	};

	const addToCart = () => {
		const cart = JSON.parse(localStorage.getItem("cart")) || [];

		const itemToAdd = {
			productName: product.name,
			variant: selectedVariant?.weights || null,
			price: selectedVariant ? selectedVariant.discounted_price : product.discounted_price,
			quantity,
			id: selectedVariant?.id || product.id,
			description: product.description,
			currency: '$',
			image: product.images[0].image_url,
		};

		const existingItemIndex = selectedVariant ? cart.findIndex(item => item.variant === itemToAdd.variant) : cart.findIndex(item => item.id === itemToAdd.id)

		if (existingItemIndex !== -1) {
			cart[existingItemIndex].quantity += quantity;
		} else {
			cart.push(itemToAdd);
		}

		localStorage.setItem("cart", JSON.stringify(cart));
		toast.success('Added to Cart', {
			position: "bottom-center",
			autoClose: 3000,
			hideProgressBar: true,
			closeOnClick: false,
			draggable: true,
			progress: undefined,
			theme: "light",
			transition: Slide,
		});
	};

	return (
		<div className="flex flex-col md:flex-row max-w-6xl mx-auto p-4 gap-6">
			{/* Image */}
			<div className="w-full md:w-1/2">
				<BreadCrumbs product={product} />
				{product && (
					<ImageCarousel
						product={product}
					/>
				)}
			</div>

			{/* Details */}
			{product && (
				<div className="w-full md:w-1/2 space-y-6 pt-5">
					{/* Tag */}
					<span className="inline-block bg-indigo-100 text-indigo-600 text-sm font-semibold px-3 py-1 rounded-full mt-10">
						{product.tag}
					</span>

					{/* Title */}
					<h1 className="text-3xl font-bold text-gray-900">
						{product.name}
					</h1>

					{/* Price */}
					<div className="flex items-center space-x-4">
						<span className="text-2xl font-semibold text-gray-900">
							${product.weights.length !== 0 ? selectedVariant.discounted_price : product.discounted_price}
						</span>
						<span className="text-lg line-through text-gray-400">
							${product.weights.length !== 0 ? selectedVariant.price : product.price}
						</span>
					</div>

					{/* Weight Unit */}
					{product.weights.length !== 0 &&
						<div>
							<h2 className="text-lg font-medium text-gray-800 mb-1">Weight Unit:</h2>
							{product.weights.map((weight) => (
								<button
									className={`inline-block border-2 bg-white text-gray-800 font-medium px-4 py-2 rounded-lg text-center min-w-[60px]
												${(selectedVariant?.weights === weight.weights) ? 'border-indigo-600' : 'border-gray-200'} mr-3
												hover:bg-gray-100 transition-colors duration-200`}
									onClick={() => onVariantButtonClick(weight.weights)}
								>
									{weight.weights}
								</button>
							))}
						</div>
					}

					{/* Quantity & Add to cart */}
					<div className="flex space-x-4">
						<select className="border rounded-md px-3 py-2" value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value))}>
							{[...Array(10)].map((_, i) => (
								<option key={i} value={i + 1}>{i + 1}</option>
							))}
						</select>
						<button
							onClick={addToCart}
							className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2 rounded-md transition"
						>
							Add to cart
						</button>
					</div>

					{/* Description */}
					<div>
						<h2 className="text-lg font-medium text-gray-800 mb-1">Description</h2>
						<p className="text-gray-700">
							{product.description}
						</p>
					</div>

					{/* Product Info */}
					<div>
						<h2 className="text-lg font-medium text-gray-800 mb-1">
							Product Information
						</h2>
						<div className="flex">
							<span className="text-gray-600 mr-2">Tag:</span>
							<span className="text-gray-800">{product.tag}</span>
						</div>
					</div>
				</div>
			)}
		</div>
	);
};

export default ProductPage;
