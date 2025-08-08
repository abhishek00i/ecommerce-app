import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
  const { isLoggedIn, loading } = useAuth();
  const location = useLocation();

  // While the auth state is being determined, don't render anything.
  // This prevents a flicker from a protected route to the login page.
  if (loading) {
    return <div>Loading...</div>; // Or a spinner component
  }

  if (!isLoggedIn) {
    // If the user is not logged in, redirect them to the login page.
    // We save the location they were trying to access in the state
    // so we can redirect them back after a successful login.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If the user is logged in, render the child routes.
  return <Outlet />;
};

export default ProtectedRoute;
