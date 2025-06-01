import React, { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import * as XLSX from 'xlsx';

function App() {
  const [customerName, setCustomerName] = useState('');
  const [customerNumber, setCustomerNumber] = useState('');
  const [customerAddress, setCustomerAddress] = useState('');
  const [billDate, setBillDate] = useState('');
  const [packingFee, setPackingFee] = useState(0);
  const [porterFee, setPorterFee] = useState(0);
  const [items, setItems] = useState([{ description: '', quantity: 1, priceINR: 0, priceUSD: 0 }]);
  const billRef = useRef(null);

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = field === 'description' ? value : parseFloat(value);
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { description: '', quantity: 1, priceINR: 0, priceUSD: 0 }]);
  };

  const generatePNG = async () => {
    const canvas = await html2canvas(billRef.current);
    const link = document.createElement('a');
    link.download = 'bill.png';
    link.href = canvas.toDataURL();
    link.click();
  };

  const generateExcel = () => {
    const itemTotalINR = items.reduce((acc, item) => acc + item.quantity * item.priceINR, 0);
    const itemTotalUSD = items.reduce((acc, item) => acc + item.quantity * item.priceUSD, 0);
    const grandTotalINR = itemTotalINR + parseFloat(packingFee) + parseFloat(porterFee);

    const data = [
      ['Date', billDate],
      ['Customer Name', customerName],
      ['Customer Number', customerNumber],
      ['Customer Address', customerAddress],
      [],
      ['Description', 'Quantity', 'Price INR', 'Price USD', 'Total INR', 'Total USD'],
      ...items.map(item => [
        item.description,
        item.quantity,
        item.priceINR,
        item.priceUSD,
        item.quantity * item.priceINR,
        item.quantity * item.priceUSD
      ]),
      [],
      ['Packing Fee (INR)', '', '', '', packingFee],
      ['Porter Fee (INR)', '', '', '', porterFee],
      ['Total INR', '', '', '', grandTotalINR],
      ['Total USD', '', '', '', '', itemTotalUSD]
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Bill');
    XLSX.writeFile(workbook, 'bill.xlsx');
  };

  const itemTotalINR = items.reduce((acc, item) => acc + item.quantity * item.priceINR, 0);
  const itemTotalUSD = items.reduce((acc, item) => acc + item.quantity * item.priceUSD, 0);
  const grandTotalINR = itemTotalINR + parseFloat(packingFee) + parseFloat(porterFee);

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <h1>Bill Generator</h1>

      <div>
        <label>Date of Bill:</label>
        <input
          type="date"
          value={billDate}
          onChange={(e) => setBillDate(e.target.value)}
          style={{ display: 'block', marginBottom: '1rem', padding: '0.5rem', width: '100%' }}
        />

        <label>Customer Name:</label>
        <input
          type="text"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          style={{ display: 'block', marginBottom: '1rem', padding: '0.5rem', width: '100%' }}
        />

        <label>Customer Number:</label>
        <input
          type="text"
          value={customerNumber}
          onChange={(e) => setCustomerNumber(e.target.value)}
          style={{ display: 'block', marginBottom: '1rem', padding: '0.5rem', width: '100%' }}
        />

        <label>Customer Address:</label>
        <textarea
          value={customerAddress}
          onChange={(e) => setCustomerAddress(e.target.value)}
          style={{ display: 'block', marginBottom: '1rem', padding: '0.5rem', width: '100%' }}
        />

        <label>Packing Fee (INR):</label>
        <input
          type="number"
          value={packingFee}
          onChange={(e) => setPackingFee(e.target.value)}
          style={{ display: 'block', marginBottom: '1rem', padding: '0.5rem' }}
        />

        <label>Porter Fee (INR):</label>
        <input
          type="number"
          value={porterFee}
          onChange={(e) => setPorterFee(e.target.value)}
          style={{ display: 'block', marginBottom: '2rem', padding: '0.5rem' }}
        />
      </div>

      {items.map((item, index) => (
        <div key={index} style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Description"
            value={item.description}
            onChange={(e) => handleItemChange(index, 'description', e.target.value)}
          />
          <input
            type="number"
            placeholder="Quantity"
            value={item.quantity}
            onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
          />
          <input
            type="number"
            placeholder="Price (INR)"
            value={item.priceINR}
            onChange={(e) => handleItemChange(index, 'priceINR', e.target.value)}
          />
          <input
            type="number"
            placeholder="Price (USD)"
            value={item.priceUSD}
            onChange={(e) => handleItemChange(index, 'priceUSD', e.target.value)}
          />
        </div>
      ))}

      <button onClick={addItem} style={{ marginBottom: '2rem' }}>Add Item</button>

      <div ref={billRef} style={{ border: '1px solid #ccc', padding: '1rem' }}>
        <h2>Bill Summary</h2>
        <p><strong>Date:</strong> {billDate}</p>
        <p><strong>Customer Name:</strong> {customerName}</p>
        <p><strong>Customer Number:</strong> {customerNumber}</p>
        <p><strong>Customer Address:</strong> {customerAddress}</p>

        <table width="100%" border="1" cellPadding="5" style={{ borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Description</th>
              <th>Qty</th>
              <th>INR</th>
              <th>USD</th>
              <th>Total INR</th>
              <th>Total USD</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => (
              <tr key={index}>
                <td>{item.description}</td>
                <td>{item.quantity}</td>
                <td>{item.priceINR}</td>
                <td>{item.priceUSD}</td>
                <td>{item.quantity * item.priceINR}</td>
                <td>{item.quantity * item.priceUSD}</td>
              </tr>
            ))}
            <tr>
              <td colSpan="4" style={{ textAlign: 'right' }}><strong>Items Total:</strong></td>
              <td>{itemTotalINR}</td>
              <td>{itemTotalUSD}</td>
            </tr>
            <tr>
              <td colSpan="4" style={{ textAlign: 'right' }}><strong>Packing Fee:</strong></td>
              <td>{packingFee}</td>
              <td>-</td>
            </tr>
            <tr>
              <td colSpan="4" style={{ textAlign: 'right' }}><strong>Porter Fee:</strong></td>
              <td>{porterFee}</td>
              <td>-</td>
            </tr>
            <tr>
              <td colSpan="4" style={{ textAlign: 'right' }}><strong>Grand Total:</strong></td>
              <td><strong>{grandTotalINR}</strong></td>
              <td><strong>{itemTotalUSD}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <button onClick={generatePNG}>Download PNG</button>
        <button onClick={generateExcel}>Download Excel</button>
      </div>
    </div>
  );
}
//Billgenerator
export default App;
 