import React from 'react';
import { Outlet, Link } from 'react-router-dom';

// Basic inline styles for layout components
const layoutStyle = {
  display: 'flex',
  height: '100vh',
  fontFamily: 'Arial, sans-serif',
};

const navStyle = {
  width: '240px',
  flexShrink: 0,
  borderRight: '1px solid #e0e0e0',
  backgroundColor: '#f7f9fc',
  padding: '20px',
};

const logoStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '30px',
    color: '#1a73e8',
};

const contentStyle = {
  flexGrow: 1,
  padding: '20px 40px',
  overflowY: 'auto',
  backgroundColor: '#ffffff',
};

const navLinkStyle = {
  display: 'block',
  padding: '12px 15px',
  margin: '8px 0',
  textDecoration: 'none',
  color: '#3c4043',
  fontWeight: 500,
  borderRadius: '8px',
  transition: 'background-color 0.2s',
};

// A simple hover effect can be managed with component state or CSS classes
// For simplicity, we'll keep it as is, but in a real app, this would be a styled component or have a .css file.

const Layout = () => {
  return (
    <div style={layoutStyle}>
      <nav style={navStyle}>
        <div style={logoStyle}>RVCourier</div>
        <Link to="/" style={navLinkStyle}>Dashboard</Link>
        <Link to="/create-shipment" style={navLinkStyle}>Create Shipment</Link>
        <Link to="/track-shipments" style={navLinkStyle}>Track Shipments</Link>
        <Link to="/all-shipments" style={navLinkStyle}>All Shipments</Link>
        <Link to="/rate-calculator" style={navLinkStyle}>Rate Calculator</Link>
        <Link to="/billing" style={navLinkStyle}>Billing & Invoices</Link>
        <Link to="/addresses" style={navLinkStyle}>Manage Addresses</Link>
        <Link to="/reports" style={navLinkStyle}>Reporting & Analytics</Link>
        <Link to="/settings" style={navLinkStyle}>Settings</Link>
      </nav>
      <main style={contentStyle}>
        {/* The Outlet component renders the matched child route's component */}
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
