import React, { useEffect, useState } from 'react';
import KPICard from '../components/KPICard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAuth } from '../context/AuthContext';
import { fetchKpis, fetchVolume } from '../services/dashboardService';

const dashboardContainerStyle = {
  display: 'flex',
  flexDirection: 'column',
};

const kpiRowStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  marginBottom: '40px',
};

const chartContainerStyle = {
  backgroundColor: '#ffffff',
  padding: '30px',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
};

const errorStyle = {
  color: 'red',
  padding: '20px',
  backgroundColor: '#ffebee',
  border: '1px solid red',
  borderRadius: '8px',
  marginBottom: '20px',
};

const DashboardPage = () => {
  const [kpis, setKpis] = useState(null);
  const [volume, setVolume] = useState([]);
  const [error, setError] = useState('');
  const { authToken } = useAuth();

  useEffect(() => {
    const loadDashboardData = async () => {
      if (authToken) {
        try {
          setError('');
          // Fetch KPI and volume data in parallel
          const [kpiData, volumeData] = await Promise.all([
            fetchKpis(authToken),
            fetchVolume(authToken),
          ]);
          setKpis(kpiData);
          setVolume(volumeData);
        } catch (err) {
          console.error("Failed to fetch dashboard data:", err);
          setError('Could not load dashboard data. Please try again later.');
        }
      }
    };

    loadDashboardData();
  }, [authToken]);

  return (
    <div style={dashboardContainerStyle}>
      <h1 style={{ marginBottom: '30px' }}>Dashboard</h1>

      {error && <div style={errorStyle}>{error}</div>}

      <div style={kpiRowStyle}>
        <KPICard title="In Transit" value={kpis ? kpis.shipments_in_transit : '...'} />
        <KPICard title="Delivered Today" value={kpis ? kpis.delivered_today : '...'} />
        <KPICard title="Pending Pickup" value={kpis ? kpis.pending_pickups : '...'} />
        <KPICard title="Delayed" value={kpis ? kpis.delayed_shipments : '...'} />
      </div>

      <div style={chartContainerStyle}>
        <h2 style={{ marginTop: 0, marginBottom: '20px' }}>Shipment Volume (Last 30 Days)</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={volume}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" name="Shipments" stroke="#1a73e8" activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DashboardPage;
