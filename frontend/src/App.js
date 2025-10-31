import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate,  useLocation, Outlet } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Reports from "./pages/Reports";
import Home from "./pages/Home";

function isTokenValid(token) {
  if (!token) return false;
  try {
    const [, payload] = token.split(".");
    if (!payload) return true; 
    const { exp } = JSON.parse(atob(payload));
    if (!exp) return true;    
    return Date.now() < exp * 1000;
  } catch {
    return true;             
  }
}

function RequireAuth() {
  const location = useLocation();
  const token = sessionStorage.getItem("access_token");

  if (!isTokenValid(token)) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return <Outlet />;
}

function PublicOnly() {
  const token = sessionStorage.getItem("access_token");
  return isTokenValid(token) ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

export default function App() {
  return (
    <div>
      
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        <Route element={<PublicOnly />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        <Route element={<RequireAuth />}>
          <Route path="dashboard" element={<Dashboard />}>
            <Route path="home" element={<Home />} />
            <Route path="reports" element={<Reports />} />
          </Route>
        </Route>

        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </div>
  );
}
