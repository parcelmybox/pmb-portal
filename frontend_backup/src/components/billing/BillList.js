import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { billingApi } from '../../services/api';

const BillList = () => {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    customer: '',
    search: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [billsResponse, customersResponse] = await Promise.all([
          billingApi.getBills(),
          billingApi.getCustomers()
        ]);
        
        // Add customer names to bills for display
        const billsWithCustomerNames = billsResponse.data.map(bill => {
          const customer = customersResponse.data.find(c => c.id === bill.customer_id);
          return {
            ...bill,
            customer_name: customer ? `${customer.first_name} ${customer.last_name}` : 'Unknown Customer',
            customer_email: customer?.email || ''
          };
        });
        
        setBills(billsWithCustomerNames);
      } catch (err) {
        setError('Failed to fetch data');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const filteredBills = bills.filter(bill => {
    return (
      (filters.status === '' || bill.status === filters.status) &&
      (filters.search === '' || 
       bill.id.toString().includes(filters.search) ||
       bill.customer_name.toLowerCase().includes(filters.search.toLowerCase()))
    );
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Bills</h1>
        <Link 
          to="/bills/create" 
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Create New Bill
        </Link>
      </div>

      <div className="bg-white shadow-md rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="search">
              Search
            </label>
            <input
              type="text"
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              placeholder="Search by ID or customer"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="status">
              Status
            </label>
            <select
              name="status"
              value={filters.status}
              onChange={handleFilterChange}
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="PAID">Paid</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="py-3 px-4 text-left">ID</th>
              <th className="py-3 px-4 text-left">Customer</th>
              <th className="py-3 px-4 text-right">Amount</th>
              <th className="py-3 px-4 text-center">Status</th>
              <th className="py-3 px-4 text-right">Date</th>
              <th className="py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredBills.length > 0 ? (
              filteredBills.map((bill) => (
                <tr key={bill.id} className="border-t hover:bg-gray-50">
                  <td className="py-3 px-4">#{bill.id}</td>
                  <td className="py-3 px-4">{bill.customer_name}</td>
                  <td className="py-3 px-4 text-right">${bill.amount}</td>
                  <td className="py-3 px-4 text-center">
                    <span 
                      className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
                        bill.status === 'PAID' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {bill.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    {new Date(bill.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <Link 
                      to={`/bills/${bill.id}`}
                      className="text-blue-500 hover:text-blue-700 mr-3"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="py-4 text-center text-gray-500">
                  No bills found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BillList;
