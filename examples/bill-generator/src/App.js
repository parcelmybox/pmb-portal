import React, { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import * as XLSX from 'xlsx';
import Navbar from './Navbar';
import './App.css';

function App() {
  const [customerName, setCustomerName] = useState('');
  const [customerNumber, setCustomerNumber] = useState('');
  const [customerAddress, setCustomerAddress] = useState('');
  const [items, setItems] = useState([{ description: '', quantity: 1, priceInINR: 0 }]);
  const [packingFee, setPackingFee] = useState(0);
  const [porterFee, setPorterFee] = useState(0);
  const [billDate, setBillDate] = useState(new Date().toISOString().substr(0, 10));
  const [exchangeRate, setExchangeRate] = useState(83.5);
  const [currency, setCurrency] = useState('INR');
  const billRef = useRef(null);

  const formatINR = (amount) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);
  const formatUSD = (amount) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    if (field === 'description') {
      newItems[index][field] = value;
    } else {
      const parsed = parseFloat(value);
      newItems[index][field] = parsed >= 0 ? parsed : 0;
    }
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { description: '', quantity: 1, priceInINR: 0 }]);
  };

  const generatePNG = async () => {
    const canvas = await html2canvas(billRef.current);
    const link = document.createElement('a');
    link.download = 'bill.png';
    link.href = canvas.toDataURL();
    link.click();
  };

  const generateExcel = () => {
    const data = [
      ['Customer Name', customerName],
      ['Customer Number', customerNumber],
      ['Customer Address', customerAddress],
      ['Bill Date', billDate],
      [],
      ['Description', 'Quantity', 'Price (INR)', 'Price (USD)', 'Total (INR)', 'Total (USD)'],
      ...items.map(item => [
        item.description,
        item.quantity,
        item.priceInINR,
        (item.priceInINR / exchangeRate).toFixed(2),
        item.quantity * item.priceInINR,
        (item.quantity * item.priceInINR / exchangeRate).toFixed(2),
      ]),
      [],
      ['Packing Fee', '', packingFee, (packingFee / exchangeRate).toFixed(2)],
      ['Porter Fee', '', porterFee, (porterFee / exchangeRate).toFixed(2)],
      ['Total', '', '', '', totalINR(), totalUSD()],
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Bill');
    XLSX.writeFile(workbook, 'bill.xlsx');
  };

  const totalINR = () =>
    items.reduce((acc, item) => acc + item.quantity * item.priceInINR, 0) +
    Number(packingFee) +
    Number(porterFee);

  const totalUSD = () => (totalINR() / exchangeRate).toFixed(2);

  return (
    <>
      <Navbar />
      <div className="form-container">
        <h1>Bill Generator</h1>

        <div className="form-group">
          <label htmlFor="customerName">Customer Name:</label>
          <input
            type="text"
            id="customerName"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="customerNumber">Customer Mobile Number:</label>
          <input
            type="tel"
            id="customerNumber"
            value={customerNumber}
            onChange={(e) => {
              const value = e.target.value;
              if (/^\d{0,10}$/.test(value)) setCustomerNumber(value);
            }}
            pattern="[0-9]{10}"
            maxLength={10}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="customerAddress">Customer Address:</label>
          <textarea
            id="customerAddress"
            rows={2}
            value={customerAddress}
            onChange={(e) => setCustomerAddress(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="billDate">Bill Date:</label>
          <input
            type="date"
            id="billDate"
            value={billDate}
            onChange={(e) => setBillDate(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="currency">Currency:</label>
          <select value={currency} onChange={(e) => setCurrency(e.target.value)} required>
            <option value="INR">INR</option>
            <option value="USD">USD</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="exchangeRate">Exchange Rate (1 USD = ? INR):</label>
          <input
            type="number"
            id="exchangeRate"
            value={exchangeRate}
            min="1"
            step="0.01"
            onChange={(e) => setExchangeRate(parseFloat(e.target.value) || 1)}
            required
          />
        </div>

        <h2>Items</h2>
        {items.map((item, index) => (
          <div className="form-group" key={index}>
            <label>Description:</label>
            <input
              type="text"
              value={item.description}
              onChange={(e) => handleItemChange(index, 'description', e.target.value)}
              required
            />
            <label>Quantity:</label>
            <input
              type="number"
              min="0"
              value={item.quantity}
              onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
              required
            />
            <label>Rate (INR):</label>
            <input
              type="number"
              min="0"
              value={item.priceInINR}
              onChange={(e) => handleItemChange(index, 'priceInINR', e.target.value)}
              required
            />
            <span>(USD: {formatUSD(item.priceInINR / exchangeRate)})</span>
          </div>
        ))}

        <button onClick={addItem}>Add Item</button>

        <div className="form-group">
          <label>Packing Fee (INR):</label>
          <input
            type="number"
            min="0"
            value={packingFee}
            onChange={(e) => setPackingFee(Math.max(0, parseFloat(e.target.value) || 0))}
            required
          />
        </div>

        <div className="form-group">
          <label>Porter Fee (INR):</label>
          <input
            type="number"
            min="0"
            value={porterFee}
            onChange={(e) => setPorterFee(Math.max(0, parseFloat(e.target.value) || 0))}
            required
          />
        </div>

        <div ref={billRef} className="bill-summary">
          <h2>Bill Summary</h2>
          <p><strong>Customer:</strong> {customerName}</p>
          <p><strong>Mobile:</strong> {customerNumber}</p>
          <p><strong>Address:</strong> {customerAddress}</p>
          <p><strong>Date:</strong> {billDate}</p>
          <table>
            <thead>
              <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Rate (INR)</th>
                <th>Rate (USD)</th>
                <th>Total (INR)</th>
                <th>Total (USD)</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => (
                <tr key={idx}>
                  <td>{item.description}</td>
                  <td>{item.quantity}</td>
                  <td>{formatINR(item.priceInINR)}</td>
                  <td>{formatUSD(item.priceInINR / exchangeRate)}</td>
                  <td>{formatINR(item.quantity * item.priceInINR)}</td>
                  <td>{formatUSD((item.quantity * item.priceInINR) / exchangeRate)}</td>
                </tr>
              ))}
              <tr>
                <td colSpan="4" style={{ textAlign: 'right' }}>Packing Fee</td>
                <td>{formatINR(packingFee)}</td>
                <td>{formatUSD(packingFee / exchangeRate)}</td>
              </tr>
              <tr>
                <td colSpan="4" style={{ textAlign: 'right' }}>Porter Fee</td>
                <td>{formatINR(porterFee)}</td>
                <td>{formatUSD(porterFee / exchangeRate)}</td>
              </tr>
              <tr>
                <td colSpan="4" style={{ textAlign: 'right' }}><strong>Total</strong></td>
                <td><strong>{formatINR(totalINR())}</strong></td>
                <td><strong>{formatUSD(totalUSD())}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="action-buttons">
          <button onClick={generatePNG}>Download PNG</button>
          <button onClick={generateExcel}>Download Excel</button>
        </div>
      </div>
    </>
  );
}

export default App;
