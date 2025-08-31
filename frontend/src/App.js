import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate,  useLocation, Outlet } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import axios from "axios";

// 如果你使用的是 JWT，可以在這裡做「是否過期」的基本檢查
function isTokenValid(token) {
  if (!token) return false;
  try {
    // 若是純字串的 opaque token（非 JWT），這段會 throw，直接視為有效交給後端判斷
    const [, payload] = token.split(".");
    if (!payload) return true; // 不是 JWT，就別在前端驗（交給後端）
    const { exp } = JSON.parse(atob(payload));
    if (!exp) return true;     // 沒 exp 視為有效
    return Date.now() < exp * 1000;
  } catch {
    return true;               // 解析失敗，多半是非 JWT，交給後端判斷
  }
}

function RequireAuth() {
  const location = useLocation();
  const token = sessionStorage.getItem("access_token");

  if (!isTokenValid(token)) {
    // 未登入或過期：導回 /login，並記住從哪裡來
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
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>

        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </div>
  );
}
