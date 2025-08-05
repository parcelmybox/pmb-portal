import React, { useState, useEffect } from 'react';

const CheckoutPage = () => {
    const [checkoutForm, setCheckoutForm] = useState({
        name: '',
        email: '',
        pickupLocation: '',
        discountCode: '',
    });

    const [shipping, setShipping] = useState('pickup');
    const [payment, setPayment] = useState('cash');
    const [total, setTotal] = useState(0);
    const [cartItems, setCartItems] = useState();

    const handleChange = (event) => {
        setCheckoutForm((prevState) => ({
            ...prevState,
            [event.target.name]: (event.target.value),
        }));
    };

    useEffect(() => {
        const cartItems = JSON.parse(localStorage.getItem('cart'));
        const newTotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        setCartItems(cartItems);
        setTotal(newTotal);
    }, []);

    return (
        <div className="flex flex-col max-w-6xl mx-auto lg:flex-row gap-10 p-10 justify-center">
            <div className="w-full lg:w-2/3 space-y-8">
                <div>
                    <h2 className="text-lg font-semibold mb-4">Checkout Details</h2>
                    <div className="space-y-4">
                        <input
                            type="text"
                            placeholder="Name"
                            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            name='name'
                            value={checkoutForm.name}
                            onChange={handleChange}
                        />
                        <input
                            type="email"
                            placeholder="E-mail"
                            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            name='email'
                            value={checkoutForm.email}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div>
                    <h2 className="text-lg font-semibold mb-4">Shipping</h2>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setShipping('pickup')}
                            className={`flex-1 border rounded px-4 py-2 text-left ${shipping === 'pickup'
                                    ? 'border-indigo-500 text-indigo-600'
                                    : 'border-gray-300'
                                }`}
                        >
                            <div className="flex justify-between">
                                <span>Pick up</span>
                                <span className="font-semibold">FREE</span>
                            </div>
                        </button>
                        <button
                            onClick={() => setShipping('delivery')}
                            className={`flex-1 border rounded px-4 py-2 text-left ${shipping === 'delivery'
                                    ? 'border-indigo-500 text-indigo-600'
                                    : 'border-gray-300 text-gray-400'
                                }`}
                            disabled
                        >
                            <div className="flex justify-between">
                                <span>
                                    Delivery <span className="font-semibold">($50.00</span> min order)
                                </span>
                                <span>$5.00</span>
                            </div>
                        </button>
                    </div>

                    <div className="mt-4">
                        <label className="block text-sm font-medium mb-1">
                            Pickup Location
                        </label>
                        <select
                            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            name='pickupLocation'
                            value={checkoutForm.pickupLocation}
                            onChange={handleChange}
                        >
                            <option>Select location</option>
                            <option>Lathrop</option>
                            <option>Tracy Hills</option>
                        </select>
                    </div>
                </div>

                <div>
                    <h2 className="text-lg font-semibold mb-4">Payment Method</h2>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setPayment('cash')}
                            className={`flex items-center gap-2 border rounded px-4 py-2 ${payment === 'cash'
                                    ? 'border-indigo-500 text-indigo-600'
                                    : 'border-gray-300'
                                }`}
                        >
                            <span className="bg-indigo-100 text-indigo-600 px-1 rounded">
                                💳
                            </span>
                            CASH
                        </button>
                    </div>
                </div>
            </div>

            <div className="w-full lg:w-1/3 bg-gray-100 p-6 rounded space-y-4">
                <h2 className="text-lg font-semibold">Order Summary</h2>

                <div className="flex items-center">
                    <input
                        type="text"
                        placeholder="Discount code"
                        className="flex-grow mt-1 w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        name='discountCode'
                        value={checkoutForm.discountCode}
                        onChange={handleChange}
                    />
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2 rounded-r-md transition">
                        Apply
                    </button>
                </div>

                <div className="flex justify-between">
                    <span>Subtotal ({cartItems && cartItems.length} Items)</span>
                    <span>${total}</span>
                </div>
                <div className="flex justify-between">
                    <span>Shipping</span>
                    <span className="text-indigo-600 font-semibold">FREE</span>
                </div>
                <hr />
                <div className="flex justify-between font-semibold text-lg">
                    <span>Total</span>
                    <span>${total}</span>
                </div>

                <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2 rounded-md transition">
                    Checkout
                </button>
            </div>
        </div>
    );
}

export default CheckoutPage;