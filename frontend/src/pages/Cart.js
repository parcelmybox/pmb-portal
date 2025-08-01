import React, { useEffect, useState } from 'react';

function Cart() {
	const [cartItems, setCartItems] = useState([]);
	const [total, setTotal] = useState(0);

	useEffect(() => {
		const cart = JSON.parse(localStorage.getItem('cart')) || [];
		setCartItems(cart);
		updateTotal();
	}, []);

	const removeFromCart = (item) => {
		const updatedItems = item.variant ? cartItems.filter((cartItem) => item.variant !== cartItem.variant) : cartItems.filter((cartItem) => item.id !== cartItem.id);
		setCartItems(updatedItems);
		localStorage.setItem('cart', JSON.stringify(updatedItems));
		updateTotal();
	};

	const updateQuantity = (item, newQuantity) => {
		const updatedItems = item.variant ? 
		cartItems.map((cartItem) => item.variant === cartItem.variant ? { ...item, quantity: newQuantity} : cartItem) :
		cartItems.map((cartItem) => item.id === cartItem.id ? { ...item, quantity: newQuantity } : cartItem);
		setCartItems(updatedItems);
		localStorage.setItem('cart', JSON.stringify(updatedItems));
		updateTotal();
	};

	const updateTotal = () => {
		const localStorageCart = JSON.parse(localStorage.getItem('cart')) || [];
		const newTotal = localStorageCart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
		setTotal(newTotal);
	};

	return (
		<div className="p-6 max-w-4xl mx-auto">
			<h1 className="text-3xl font-bold text-gray-800 mb-8">International Shipping Cart</h1>
			{/* Cart Items */}
			<div className="bg-white rounded-lg shadow-lg p-6">
				<h2 className="text-2xl font-semibold text-gray-800 mb-6">Your Cart</h2>

				{cartItems.length === 0 ? (
					<p className="text-gray-600">Your cart is empty</p>
				) : (
					<div className="space-y-4">
						{cartItems.map((item) => (
							<div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
								<div>
									<h3 className="font-medium text-gray-800">
										{item.productName}<span className='font-normal'>{item.variant && ` - ${item.variant}`}</span>
									</h3>
									<p className="text-sm text-gray-600">{item.description}</p>
								</div>
								<div className="flex items-center space-x-4">
									<div className="flex items-center">
										<button
											onClick={() => updateQuantity(item, item.quantity - 1)}
											disabled={item.quantity === 1}
											className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200"
										> 
											-
										</button>
										<span className="mx-2">{item.quantity}</span>
										<button
											onClick={() => updateQuantity(item, item.quantity + 1)}
											className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200"
										>
											+
										</button>
									</div>
									<div className="flex items-center space-x-2">
										<p className="text-indigo-600 font-medium">{item.currency}{(item.price * item.quantity).toLocaleString()}</p>
										<button
											onClick={() => removeFromCart(item)}
											className="text-red-500 hover:text-red-700"
										>
											Remove
										</button>
									</div>
								</div>
							</div>
						))}

						<div className="border-t pt-6">
							<div className="flex justify-between items-center">
								<div className="flex items-center justify-end space-x-4 mt-6">
									<p className="text-2xl font-bold text-indigo-600">Total: ${total.toLocaleString()}</p>
								</div>
							</div>
							<button
								className="w-full mt-4 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700"
								disabled={cartItems.length === 0}
							>
								Proceed to Checkout
							</button>
						</div>
					</div>
				)}
			</div>
		</div>
	);
}

export default Cart;
