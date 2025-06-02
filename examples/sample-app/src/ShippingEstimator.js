// ShippingEstimator.js
import React, { useState } from 'react';

export default function ShippingEstimator() {
  const [pickup, setPickup] = useState('Hyderabad');
  const [carrier, setCarrier] = useState('DHL');
  const [packageType, setPackageType] = useState('Document');
  const [zip, setZip] = useState('95330');
  const [length, setLength] = useState('');
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [unit, setUnit] = useState('cm');
  const [result, setResult] = useState(null);

  const calculateShipping = () => {
    let price, days;
    if (packageType === 'Document') {
      switch (carrier) {
        case 'DHL': price = 3000; days = 3; break;
        case 'FedEx': price = 2500; days = 5; break;
        case 'UPS': price = 2400; days = 7; break;
        default: price = 0; days = 0;
      }
      setResult({ carrier, packageType, price: `₹${price}`, days });
    } else {
      const l = parseFloat(length);
      const w = parseFloat(width);
      const h = parseFloat(height);

      if (isNaN(l) || isNaN(w) || isNaN(h)) {
        setResult({ error: 'Please enter valid box dimensions.' });
        return;
      }

      let volumetricWeight;
      if (unit === 'cm') {
        volumetricWeight = (l * w * h) / 5000;
      } else {
        volumetricWeight = (l * w * h) / 139;
      }
      setResult({
        carrier,
        packageType,
        volumetricWeight: volumetricWeight.toFixed(2) + (unit === 'cm' ? ' kg' : ' lbs')
      });
    }
  };

  return (
    <div className="estimator-container">
      <h2>Shipping Estimator</h2>

      <label>Pickup City</label>
      <select value={pickup} onChange={e => setPickup(e.target.value)}>
        <option value="Hyderabad">Hyderabad</option>
        <option value="Chennai">Chennai</option>
      </select>

      <label>Carrier</label>
      <select value={carrier} onChange={e => setCarrier(e.target.value)}>
        <option value="DHL">DHL</option>
        <option value="FedEx">FedEx</option>
        <option value="UPS">UPS</option>
      </select>

      <label>Package Type</label>
      <select value={packageType} onChange={e => setPackageType(e.target.value)}>
        <option value="Document">Document</option>
        <option value="Box">Box</option>
      </select>

      <label>Destination Zip Code</label>
      <input
        type="text"
        value={zip}
        onChange={e => setZip(e.target.value)}
        placeholder="e.g. 95330"
      />

      {packageType === 'Box' && (
        <div className="box-inputs">
          <label>Length ({unit})</label>
          <input type="number" value={length} onChange={e => setLength(e.target.value)} />

          <label>Width ({unit})</label>
          <input type="number" value={width} onChange={e => setWidth(e.target.value)} />

          <label>Height ({unit})</label>
          <input type="number" value={height} onChange={e => setHeight(e.target.value)} />

          <label>Unit</label>
          <select value={unit} onChange={e => setUnit(e.target.value)}>
            <option value="cm">Centimeters (cm)</option>
            <option value="inch">Inches (in)</option>
          </select>
        </div>
      )}

      <button onClick={calculateShipping}>Estimate Shipping</button>

      {result && (
        <div className="result">
          {result.error ? (
            <p style={{ color: 'red' }}>{result.error}</p>
          ) : (
            <>
              <p><strong>Carrier:</strong> {result.carrier}</p>
              <p><strong>Package Type:</strong> {result.packageType}</p>
              {result.price && <p><strong>Estimated Price:</strong> {result.price}</p>}
              {result.days && <p><strong>Estimated Delivery:</strong> {result.days} days</p>}
              {result.volumetricWeight && <p><strong>Volumetric Weight:</strong> {result.volumetricWeight}</p>}
            </>
          )}
        </div>
      )}
    </div>
  );
}
