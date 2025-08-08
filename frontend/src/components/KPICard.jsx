import React from 'react';

const kpiCardStyle = {
  backgroundColor: '#ffffff',
  padding: '20px 25px',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  flex: '1',
  margin: '0 10px',
  textAlign: 'left',
};

const kpiValueStyle = {
  fontSize: '32px',
  fontWeight: 'bold',
  margin: '0 0 5px 0',
  color: '#202124',
};

const kpiTitleStyle = {
  fontSize: '14px',
  color: '#5f6368',
  margin: '0',
  textTransform: 'uppercase',
};

const KPICard = ({ title, value }) => {
  return (
    <div style={kpiCardStyle}>
      <p style={kpiValueStyle}>{value !== null ? value : '...'}</p>
      <p style={kpiTitleStyle}>{title}</p>
    </div>
  );
};

export default KPICard;
