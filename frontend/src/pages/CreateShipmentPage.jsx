import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { createShipment } from '../services/shipmentService';

// (Styles remain the same)
const pageStyle = { maxWidth: '900px' };
const formStyle = { display: 'flex', flexDirection: 'column', gap: '30px' };
const sectionStyle = { backgroundColor: '#ffffff', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' };
const sectionTitleStyle = { marginTop: 0, marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px', fontSize: '18px', color: '#333' };
const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' };
const inputGroupStyle = { display: 'flex', flexDirection: 'column', gap: '5px' };
const inputStyle = { padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' };
const buttonStyle = { padding: '15px 25px', fontSize: '16px', backgroundColor: '#1a73e8', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', alignSelf: 'flex-start' };
const notificationStyle = { padding: '15px', borderRadius: '8px', marginBottom: '20px', color: 'white' };
const successStyle = { ...notificationStyle, backgroundColor: '#28a745' };
const errorStyle = { ...notificationStyle, backgroundColor: '#dc3545' };


const CreateShipmentPage = () => {
  const initialFormData = {
    sender_address: { contact_name: '', contact_phone: '', address_line_1: '', city: '', state: '', pincode: '' },
    recipient_address: { contact_name: '', contact_phone: '', address_line_1: '', city: '', state: '', pincode: '' },
    package_length: '', package_width: '', package_height: '', package_weight: '',
    contents: '', invoice_value: '', carrier_id: ''
  };

  const [formData, setFormData] = useState(initialFormData);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ type: '', message: '' });
  const { authToken } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    const keys = name.split('.');
    if (keys.length === 2) {
      const [objKey, fieldKey] = keys;
      setFormData(prev => ({ ...prev, [objKey]: { ...prev[objKey], [fieldKey]: value } }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setNotification({ type: '', message: '' });

    try {
      const result = await createShipment(formData, authToken);
      setNotification({ type: 'success', message: `Shipment created successfully with ID: ${result.id}` });
      setFormData(initialFormData); // Reset form on success
    } catch (error) {
      const message = error.response?.data?.detail || 'An unexpected error occurred. Please try again.';
      setNotification({ type: 'error', message });
      console.error("Failed to create shipment:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={pageStyle}>
      <h1 style={{ marginBottom: '30px' }}>Create New Shipment</h1>

      {notification.message && (
        <div style={notification.type === 'success' ? successStyle : errorStyle}>
          {notification.message}
        </div>
      )}

      <form style={formStyle} onSubmit={handleSubmit}>
        {/* --- Sender Details --- */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>Sender Details</h3>
          <div style={gridStyle}>
            <div style={inputGroupStyle}><label>Contact Name</label><input required style={inputStyle} name="sender_address.contact_name" value={formData.sender_address.contact_name} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Phone</label><input required style={inputStyle} name="sender_address.contact_phone" value={formData.sender_address.contact_phone} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Address Line 1</label><input required style={inputStyle} name="sender_address.address_line_1" value={formData.sender_address.address_line_1} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>City</label><input required style={inputStyle} name="sender_address.city" value={formData.sender_address.city} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>State</label><input required style={inputStyle} name="sender_address.state" value={formData.sender_address.state} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Pincode</label><input required style={inputStyle} name="sender_address.pincode" value={formData.sender_address.pincode} onChange={handleChange} /></div>
          </div>
        </div>

        {/* --- Recipient Details --- */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>Recipient Details</h3>
          <div style={gridStyle}>
            <div style={inputGroupStyle}><label>Contact Name</label><input required style={inputStyle} name="recipient_address.contact_name" value={formData.recipient_address.contact_name} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Phone</label><input required style={inputStyle} name="recipient_address.contact_phone" value={formData.recipient_address.contact_phone} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Address Line 1</label><input required style={inputStyle} name="recipient_address.address_line_1" value={formData.recipient_address.address_line_1} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>City</label><input required style={inputStyle} name="recipient_address.city" value={formData.recipient_address.city} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>State</label><input required style={inputStyle} name="recipient_address.state" value={formData.recipient_address.state} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Pincode</label><input required style={inputStyle} name="recipient_address.pincode" value={formData.recipient_address.pincode} onChange={handleChange} /></div>
          </div>
        </div>

        {/* --- Package Details --- */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>Package Details</h3>
          <div style={gridStyle}>
            <div style={inputGroupStyle}><label>Weight (kg)</label><input required style={inputStyle} type="number" name="package_weight" value={formData.package_weight} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Length (cm)</label><input required style={inputStyle} type="number" name="package_length" value={formData.package_length} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Width (cm)</label><input required style={inputStyle} type="number" name="package_width" value={formData.package_width} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Height (cm)</label><input required style={inputStyle} type="number" name="package_height" value={formData.package_height} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Contents</label><input required style={inputStyle} name="contents" value={formData.contents} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Invoice Value (₹)</label><input required style={inputStyle} type="number" name="invoice_value" value={formData.invoice_value} onChange={handleChange} /></div>
            <div style={inputGroupStyle}><label>Carrier ID</label><input required style={inputStyle} type="number" name="carrier_id" value={formData.carrier_id} onChange={handleChange} /></div>
          </div>
        </div>

        <button type="submit" style={buttonStyle} disabled={loading}>
          {loading ? 'Booking...' : 'Book Shipment'}
        </button>
      </form>
    </div>
  );
};

export default CreateShipmentPage;
