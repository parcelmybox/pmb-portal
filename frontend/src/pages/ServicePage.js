import React from "react";
import ImageCarousel from "../components/ImageCarousel";
import BreadCrumbs from "../components/BreadCrumbs";

const ServicePage = () => {
	return (
		<div className="flex flex-col md:flex-row max-w-6xl mx-auto p-4 gap-6">
			{/* Image */}
			<div className="w-full md:w-1/2">
				<BreadCrumbs />
				<ImageCarousel
					images={[
						{ name: 'Lotus', src: 'https://cdn.store.link/products/deliveryhub/3yefvf-pink%20lotus%20thuumbnail.jpg?versionId=GxIFTAHpxLkDEWwirUAUo9QtqHrRwekx' },
						{ name: 'Lotus', src: 'https://cdn.store.link/products/deliveryhub/iv6wxp-pink-lotus-flower.jpg?versionId=HD2F_NWFlTJd_NdpAh9d1y0EHAf3jmMB' }
					]}
				/>
			</div>

			{/* Details */}
			<div className="w-full md:w-1/2 space-y-6">
				{/* Tag */}
				<span className="inline-block bg-indigo-100 text-indigo-600 text-sm font-semibold px-3 py-1 rounded-full mt-10">
					USA2INDIA
				</span>

				{/* Title */}
				<h1 className="text-3xl font-bold text-gray-900">
					FedEx Document Shipping
				</h1>

				{/* Price */}
				<div className="flex items-center space-x-4">
					<span className="text-2xl font-semibold text-gray-900">$65.00</span>
					<span className="text-lg line-through text-gray-400">$125.00</span>
				</div>

				{/* Quantity & Add to cart */}
				<div className="flex space-x-4">
					<select className="border rounded-md px-3 py-2" defaultValue={1}>
						{[...Array(10)].map((_, i) => (
							<option key={i}>{i + 1}</option>
						))}
					</select>
					<button className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2 rounded-md transition">
						Add to cart
					</button>
				</div>

				{/* Description */}
				<div>
					<h2 className="text-lg font-medium text-gray-800 mb-1">Description</h2>
					<p className="text-gray-700">
						Document shipping FedEx Express. 5 day shipping to your destination in India
					</p>
				</div>

				{/* Product Info */}
				<div>
					<h2 className="text-lg font-medium text-gray-800 mb-1">
						Product Information
					</h2>
					<div className="flex">
						<span className="text-gray-600 mr-2">Tag:</span>
						<span className="text-gray-800">USA2INDIA</span>
					</div>
				</div>
			</div>
		</div>
	);
};

export default ServicePage;
