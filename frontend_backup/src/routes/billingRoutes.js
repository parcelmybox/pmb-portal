import React from 'react';
import { Routes, Route } from 'react-router-dom';
import BillList from '../components/billing/BillList';
import BillForm from '../components/billing/BillForm';
import BillDetail from '../components/billing/BillDetail';

const BillingRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<BillList />} />
      <Route path="/create" element={<BillForm />} />
      <Route path="/:id" element={<BillDetail />} />
      <Route path="/:id/edit" element={<BillForm />} />
    </Routes>
  );
};

export default BillingRoutes;
