import React, { useState } from 'react';

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [total, setTotal] = useState(0);

  const sampleItems = [
    {
      id: 1,
      name: 'Standard Shipping',
      price: 4999,
      description: 'India to USA - Up to 5kg, delivery within 10-15 business days',
      quantity: 1,
      currency: '₹'
    },
    {
      id: 2,
      name: 'Priority Shipping',
      price: 8999,
      description: 'India to USA - Up to 10kg, delivery within 7-10 business days',
      quantity: 1,
      currency: '₹'
    },
    {
      id: 3,
      name: 'International Insurance',
      price: 1000,
      description: 'Up to ₹10,000 coverage for international shipments',
      quantity: 1,
      currency: '₹'
    },
    {
      id: 4,
      name: 'Standard Shipping',
      price: 7999,
      description: 'USA to India - Up to 5kg, delivery within 10-15 business days',
      quantity: 1,
      currency: '₹'
    },
    {
      id: 5,
      name: 'Priority Shipping',
      price: 14999,
      description: 'USA to India - Up to 10kg, delivery within 7-10 business days',
      quantity: 1,
      currency: '₹'
    }
  ];

  const addToCart = (item) => {
    const existingItem = cartItems.find((i) => i.id === item.id);
    if (existingItem) {
      const updatedItems = cartItems.map((i) =>
        i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
      );
      setCartItems(updatedItems);
    } else {
      setCartItems([...cartItems, { ...item, quantity: 1 }]);
    }
    updateTotal();
  };

  const removeFromCart = (itemId) => {
    const updatedItems = cartItems.filter((item) => item.id !== itemId);
    setCartItems(updatedItems);
    updateTotal();
  };

  const updateQuantity = (itemId, newQuantity) => {
    const updatedItems = cartItems.map((item) =>
      item.id === itemId ? { ...item, quantity: newQuantity } : item
    );
    setCartItems(updatedItems);
    updateTotal();
  };

  const updateTotal = () => {
    const newTotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    setTotal(newTotal);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">International Shipping Cart</h1>

      {/* Available Services */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Available International Shipping Services</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {sampleItems.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-md p-4">
              <h3 className="text-lg font-medium text-gray-800 mb-2">{item.name}</h3>
              <p className="text-gray-600 mb-2">{item.description}</p>
              <p className="text-indigo-600 font-medium mb-4">{item.currency}{item.price.toLocaleString()}</p>
              <button
                onClick={() => addToCart(item)}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700"
              >
                Add to Cart
              </button>
            </div>
          ))}
        </div>
      </div>

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
                  <h3 className="font-medium text-gray-800">{item.name}</h3>
                  <p className="text-sm text-gray-600">{item.description}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      disabled={item.quantity === 1}
                      className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200"
                    >
                      -
                    </button>
                    <span className="mx-2">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200"
                    >
                      +
                    </button>
                  </div>
                  <div className="flex items-center space-x-2">
                    <p className="text-indigo-600 font-medium">{item.currency}{(item.price * item.quantity).toLocaleString()}</p>
                    <button
                      onClick={() => removeFromCart(item.id)}
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
                  <p className="text-2xl font-bold text-indigo-600">Total: ₹{total.toLocaleString()}</p>
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
