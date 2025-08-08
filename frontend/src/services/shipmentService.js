import api from './api';

/**
 * Creates a new shipment by sending data to the backend API.
 * @param {object} shipmentData - The shipment data from the form.
 * @param {string} token - The user's JWT authentication token.
 * @returns {Promise<object>} A promise that resolves to the data of the newly created shipment.
 */
export const createShipment = async (shipmentData, token) => {
  // The backend API expects numeric types for certain fields.
  // HTML form inputs usually provide strings, so we must convert them.
  const payload = {
    ...shipmentData,
    package_length: parseFloat(shipmentData.package_length) || 0,
    package_width: parseFloat(shipmentData.package_width) || 0,
    package_height: parseFloat(shipmentData.package_height) || 0,
    package_weight: parseFloat(shipmentData.package_weight) || 0,
    invoice_value: parseFloat(shipmentData.invoice_value) || 0,
    carrier_id: parseInt(shipmentData.carrier_id, 10) || 0,
  };

  const response = await api.post('/shipments/', payload, {
    headers: { Authorization: `Bearer ${token}` },
  });

  return response.data;
};

/**
 * Fetches a list of shipments, with optional filters.
 * @param {object} filters - An object containing filter parameters (e.g., { status: 'Delivered' }).
 * @param {string} token - The user's JWT authentication token.
 * @returns {Promise<Array<object>>} A promise that resolves to an array of shipment objects.
 */
export const getShipments = async (filters = {}, token) => {
  const params = new URLSearchParams();

  // Append filters to params if they exist
  if (filters.status) params.append('status', filters.status);
  if (filters.carrier_id) params.append('carrier_id', filters.carrier_id);
  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);
  if (filters.sort_by) params.append('sort_by', filters.sort_by);

  const response = await api.get('/shipments/', {
    headers: { Authorization: `Bearer ${token}` },
    params,
  });

  return response.data;
};
