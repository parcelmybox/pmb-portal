import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { billingApi } from '../../services/api';
import { ArrowLeftIcon, PencilIcon } from '@heroicons/react/24/outline';

const BillDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [bill, setBill] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [billRes, activitiesRes] = await Promise.all([
          billingApi.getBill(id),
          billingApi.getBillActivities(id)
        ]);
        
        // Format the bill data with customer info
        const customer = billRes.data.customer || {};
        const formattedBill = {
          ...billRes.data,
          customer_name: customer.first_name && customer.last_name 
            ? `${customer.first_name} ${customer.last_name}` 
            : 'Unknown Customer',
          customer_email: customer.email || ''
        };
        
        setBill(formattedBill);
        setActivities(activitiesRes.data || []);
      } catch (err) {
        setError('Failed to load bill details');
        console.error('Error fetching bill details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleStatusUpdate = async (newStatus) => {
    if (!window.confirm(`Are you sure you want to mark this bill as ${newStatus.toLowerCase()}?`)) {
      return;
    }

    try {
      setUpdatingStatus(true);
      
      // Update the bill status
      const updatedBill = { ...bill, status: newStatus };
      await billingApi.updateBill(id, updatedBill);
      
      // Update local state
      setBill(prev => ({
        ...prev,
        status: newStatus,
        updated_at: new Date().toISOString()
      }));
      
      // Refresh activities to get the latest
      const activitiesRes = await billingApi.getBillActivities(id);
      setActivities(activitiesRes.data || []);
      
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!bill) return <div className="p-4">Bill not found</div>;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = (status) => {
    const baseClasses = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium';
    
    switch (status) {
      case 'PAID':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'PENDING':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <Link 
          to="/bills" 
          className="inline-flex items-center text-blue-500 hover:text-blue-700"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Bills
        </Link>
      </div>
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Bill #{bill.id}</h1>
              <p className="text-gray-600">
                Created on {formatDate(bill.created_at)}
              </p>
            </div>
            <div className="flex space-x-2">
              <Link
                to={`/bills/${id}/edit`}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <PencilIcon className="h-4 w-4 mr-1" />
                Edit
              </Link>
              {bill.status === 'PENDING' && (
                <button
                  onClick={() => handleStatusUpdate('PAID')}
                  disabled={updatingStatus}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {updatingStatus ? 'Updating...' : 'Mark as Paid'}
                </button>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-2">Bill To</h2>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="font-medium">{bill.customer_name}</p>
                <p className="text-gray-600">{bill.customer_email}</p>
              </div>
            </div>
            
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-2">Status</h2>
              <div className="p-4">
                <span className={getStatusBadge(bill.status)}>
                  {bill.status}
                </span>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Bill Details</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {bill.description || 'Bill amount'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                      ${parseFloat(bill.amount).toFixed(2)}
                    </td>
                  </tr>
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900" colSpan="2">
                      <span className="mr-4">Total:</span>
                      <span className="text-lg">${parseFloat(bill.amount).toFixed(2)}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Activity Log</h2>
          <div className="space-y-4">
            {activities.length > 0 ? (
              activities.map((activity) => (
                <div key={activity.id} className="flex items-start pb-4 border-b border-gray-100 last:border-0">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-blue-600 font-medium">
                      {activity.user?.username?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="ml-4">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {activity.user?.username || 'System'}
                      </p>
                      <span className="mx-1 text-gray-500">•</span>
                      <p className="text-sm text-gray-500">
                        {formatDate(activity.created_at)}
                      </p>
                    </div>
                    <p className="text-sm text-gray-700 mt-1">
                      {activity.description}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No activity recorded for this bill.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillDetail;
