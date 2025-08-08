import api from './api';

/**
 * Fetches the dashboard KPI data from the backend.
 * @param {string} token The JWT authentication token.
 * @returns {Promise<object>} A promise that resolves to the KPI data.
 */
export const fetchKpis = async (token) => {
  const response = await api.get('/dashboard/kpis', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

/**
 * Fetches the shipment volume data for the last 30 days.
 * @param {string} token The JWT authentication token.
 * @returns {Promise<Array<object>>} A promise that resolves to the volume data array.
 */
export const fetchVolume = async (token) => {
  const response = await api.get('/dashboard/shipment-volume', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};
