import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { getShipments } from '../services/shipmentService';

// (Styles remain the same)
const pageStyle = { display: 'flex', flexDirection: 'column', gap: '30px' };
const filterBarStyle = { display: 'flex', gap: '20px', padding: '20px', backgroundColor: '#ffffff', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', alignItems: 'center' };
const tableContainerStyle = { backgroundColor: '#ffffff', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', overflow: 'hidden' };
const tableStyle = { width: '100%', borderCollapse: 'collapse' };
const thTdStyle = { padding: '12px 15px', textAlign: 'left', borderBottom: '1px solid #ddd' };
const thStyle = { ...thTdStyle, backgroundColor: '#f8f9fa', fontWeight: 'bold' };
const inputStyle = { padding: '8px 12px', borderRadius: '4px', border: '1px solid #ccc' };
const buttonStyle = { padding: '8px 20px', borderRadius: '4px', border: 'none', backgroundColor: '#1a73e8', color: 'white', cursor: 'pointer' };

const AllShipmentsPage = () => {
  const [shipments, setShipments] = useState([]);
  const [filters, setFilters] = useState({ status: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { authToken } = useAuth();

  const fetchShipments = useCallback(async () => {
    if (!authToken) return;
    setLoading(true);
    setError('');
    try {
      const data = await getShipments(filters, authToken);
      setShipments(data);
    } catch (err) {
      console.error("Failed to fetch shipments:", err);
      setError("Could not load shipments.");
    } finally {
      setLoading(false);
    }
  }, [authToken, filters]);

  useEffect(() => {
    fetchShipments();
  }, [fetchShipments]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchShipments();
  };

  return (
    <div style={pageStyle}>
      <h1>All Shipments</h1>

      <form style={filterBarStyle} onSubmit={handleFilterSubmit}>
        <input
          type="text"
          name="status"
          placeholder="Filter by Status..."
          style={inputStyle}
          value={filters.status}
          onChange={handleFilterChange}
        />
        {/* Add more filters for date, carrier etc. here */}
        <button type="submit" style={buttonStyle}>Filter</button>
      </form>

      {loading && <p>Loading shipments...</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}

      <div style={tableContainerStyle}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>AWB Number</th>
              <th style={thStyle}>Carrier</th>
              <th style={thStyle}>From</th>
              <th style={thStyle}>To</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Created At</th>
            </tr>
          </thead>
          <tbody>
            {!loading && shipments.length === 0 && (
              <tr><td colSpan="6" style={{textAlign: 'center', padding: '20px'}}>No shipments found.</td></tr>
            )}
            {shipments.map((shipment) => (
              <tr key={shipment.id}>
                <td style={thTdStyle}>{shipment.awb_number || 'N/A'}</td>
                <td style={thTdStyle}>{shipment.carrier.name}</td>
                <td style={thTdStyle}>{shipment.sender_address.city}</td>
                <td style={thTdStyle}>{shipment.recipient_address.city}</td>
                <td style={thTdStyle}>{shipment.status}</td>
                <td style={thTdStyle}>{new Date(shipment.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AllShipmentsPage;
