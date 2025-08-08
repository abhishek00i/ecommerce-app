import axios from 'axios';

// Create a dedicated axios instance for our API
const api = axios.create({
  baseURL: 'http://localhost:8000', // The address of our FastAPI backend
});

// You can also add interceptors here for handling tokens automatically
// or for global error handling, but we'll keep it simple for now.

export default api;
