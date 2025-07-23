import React, { useState, useEffect } from 'react';

// const images = [
// 	{
// 		id: 1,
// 		src: 'https://cdn.store.link/products/deliveryhub/3yefvf-pink%20lotus%20thuumbnail.jpg?versionId=GxIFTAHpxLkDEWwirUAUo9QtqHrRwekx',
// 		alt: 'Flower 1',
// 	},
// 	{
// 		id: 2,
// 		src: 'https://cdn.store.link/products/deliveryhub/iv6wxp-pink-lotus-flower.jpg?versionId=HD2F_NWFlTJd_NdpAh9d1y0EHAf3jmMB',
// 		alt: 'Flower 2',
// 	},
// ];



const ImageCarousel = (props) => {
	const [images, setImages] = useState([]);
	const [selectedImage, setSelectedImage] = useState(0);

	useEffect(() => {
		let counter = 0;
		const imagesDict = props.images.map(image => {
			return {
				id: counter, 
				src: image.src,
				alt: `${image.name} Image ${counter++}`
			}
		})
		setImages(imagesDict);
	}, []);

	return (
		<div className="flex flex-col items-center space-y-4">
			{/* Main Image */}
			{images.length !== 0 && (
				<div className="w-full max-w-2xl">
					<img
						src={images[selectedImage].src}
						alt={images[selectedImage].alt}
						className="rounded-lg shadow-md w-full h-auto object-contain"
					/>
				</div>
			)}

			{/* Thumbnail Carousel */}
			<div className="flex space-x-4">
				{images.length !== 0 && images.map((img) => (
					<button
						key={img.id}
						onClick={() => setSelectedImage(img.id)}
						className={`border-2 rounded-lg overflow-hidden p-1 transition-transform duration-300 ${selectedImage === img.id
								? 'border-indigo-600 scale-105'
								: 'border-transparent'
							}`}
					>
						<img
							src={img.src}
							alt={img.alt}
							className="w-20 h-20 object-cover rounded"
						/>
					</button>
				))}
			</div>
		</div>
	);
}

export default ImageCarousel;