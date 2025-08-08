import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Layout and Auth Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Page Components
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CreateShipmentPage from './pages/CreateShipmentPage';

import './App.css';

// Placeholder components for pages not yet created
const TrackShipmentsPage = () => <h1>Track Shipments</h1>;
const AllShipmentsPage = () => <h1>All Shipments</h1>;
const RateCalculatorPage = () => <h1>Rate Calculator</h1>;
const BillingPage = () => <h1>Billing & Invoices</h1>;
const AddressesPage = () => <h1>Manage Addresses</h1>;
const ReportsPage = () => <h1>Reporting & Analytics</h1>;
const SettingsPage = () => <h1>Settings</h1>;
const NotFoundPage = () => <h1>404 - Not Found</h1>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public route for login */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes that are part of the main application layout */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="create-shipment" element={<CreateShipmentPage />} />
            <Route path="track-shipments" element={<TrackShipmentsPage />} />
            <Route path="all-shipments" element={<AllShipmentsPage />} />
            <Route path="rate-calculator" element={<RateCalculatorPage />} />
            <Route path="billing" element={<BillingPage />} />
            <Route path="addresses" element={<AddressesPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
