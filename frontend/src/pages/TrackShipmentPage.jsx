import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getShipmentByAwb } from '../services/shipmentService';

// (Styles remain the same)
const pageStyle = { maxWidth: '800px' };
const formStyle = { display: 'flex', gap: '10px', marginBottom: '40px' };
const inputStyle = { flexGrow: 1, padding: '12px', fontSize: '16px', borderRadius: '4px', border: '1px solid #ccc' };
const buttonStyle = { padding: '12px 25px', fontSize: '16px', backgroundColor: '#1a73e8', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' };
const resultContainerStyle = { backgroundColor: '#ffffff', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' };
const timelineStyle = { listStyle: 'none', padding: 0, marginTop: '20px' };
const timelineItemStyle = { padding: '15px 10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' };
const errorStyle = { color: 'orange', marginTop: '20px' };

const TrackShipmentPage = () => {
  const [awb, setAwb] = useState('');
  const [shipment, setShipment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { authToken } = useAuth();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!awb) return;

    setLoading(true);
    setError('');
    setShipment(null);

    try {
      const data = await getShipmentByAwb(awb, authToken);
      setShipment(data);
    } catch (err) {
      console.error("Failed to track shipment:", err);
      if (err.response && err.response.status === 404) {
        setError(`No shipment found with AWB number: ${awb}`);
      } else {
        setError("An error occurred while tracking the shipment.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={pageStyle}>
      <h1>Track Your Shipment</h1>
      <p>Enter your Air Waybill (AWB) number to see the latest tracking updates.</p>

      <form style={formStyle} onSubmit={handleSearch}>
        <input
          style={inputStyle}
          type="text"
          placeholder="e.g., 123456789"
          value={awb}
          onChange={(e) => setAwb(e.target.value)}
        />
        <button style={buttonStyle} type="submit" disabled={loading}>
          {loading ? 'Tracking...' : 'Track'}
        </button>
      </form>

      {loading && <p>Searching for your shipment...</p>}
      {error && <div style={errorStyle}>{error}</div>}

      {shipment && (
        <div style={resultContainerStyle}>
          <h2>Tracking Details for AWB: {shipment.awb_number}</h2>
          <p><strong>Current Status:</strong> {shipment.status}</p>
          <hr />
          <h3>History</h3>
          <ul style={timelineStyle}>
            {shipment.deliveries.length > 0 ? (
              shipment.deliveries.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).map((event) => (
                <li key={event.id} style={timelineItemStyle}>
                  <div>
                    <strong>{event.status}</strong>
                    {event.location && <span style={{color: '#555'}}> - {event.location}</span>}
                  </div>
                  <span style={{color: '#777'}}>{new Date(event.timestamp).toLocaleString()}</span>
                </li>
              ))
            ) : (
              <li>No tracking history available yet.</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default TrackShipmentPage;
