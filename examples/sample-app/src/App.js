// App.js
import React from 'react';
import Navbar from './navbar';
import ShippingEstimator from './ShippingEstimator';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <ShippingEstimator />
    </div>
  );
}
