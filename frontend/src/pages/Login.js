import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import styles from "./Login.module.css"; // 引入 CSS 模塊

function isTokenValid(t) {
  if (!t) return false;
  try {
    const [, payload] = t.split(".");
    if (!payload) return true; // 非 JWT：交給後端驗
    const { exp } = JSON.parse(atob(payload)); // 解析 exp（秒）
    return !exp || Date.now() < exp * 1000;
  } catch {
    return true; // 不是標準 JWT 就視為交給後端
  }
}

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  // 頁面載入時加入特定的 body 樣式
  useEffect(() => {
    document.body.classList.add(styles.loginBody); // 為 body 添加 Login 頁面樣式

    return () => {
      document.body.classList.remove(styles.loginBody); // 清除 body 樣式
    };
  }, []);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (isTokenValid(t)) {
      const from = location.state?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    }
  }, [location, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("/auth/login", { email, password });
      sessionStorage.setItem("access_token", response.data.access_token);
      const from = location.state?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    } catch (error) {
      console.error("login error", error.response?.status, error.response?.data, error.message);
      alert(error.response?.data?.detail || "invalid credentials");
    }
  };

  const goRegister = () => {
    navigate("/register");
  };

  return (
    <>
      <div className={styles.LoginpageTitle}>
        <h1 className={styles.LoginheroTitle}>Bank Linker</h1>
        <p className={styles.LoginheroSubtitle}></p>
      </div>

      <div className={styles.LoginContainer}>
        <h2>Log In</h2>
        <form onSubmit={handleLogin}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <button type="LoginSubmitButton">Login</button>
          <button type="RegisterButton" onClick={goRegister}>Sign Up For Free</button>
        </form>
      </div>
    </>
  );
};

export default Login;
