import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const DynamicCSS = () => {
  const location = useLocation();

  useEffect(() => {
    // 根據路由加載對應的CSS文件
    let linkElement = null;

    if (location.pathname === "/login") {
      linkElement = document.createElement("link");
      linkElement.rel = "stylesheet";
      linkElement.href = "/path/to/Login.css";  // 替換為實際的CSS路徑
      document.head.appendChild(linkElement);
    } else if (location.pathname === "/register") {
      linkElement = document.createElement("link");
      linkElement.rel = "stylesheet";
      linkElement.href = "/path/to/Register.css";  // 替換為實際的CSS路徑
      document.head.appendChild(linkElement);
    } else if (location.pathname === "/dashboard") {
      linkElement = document.createElement("link");
      linkElement.rel = "stylesheet";
      linkElement.href = "/path/to/Dashboard.css";  // 替換為實際的CSS路徑
      document.head.appendChild(linkElement);
    }

    // 清理工作：當離開頁面時，移除CSS
    return () => {
      if (linkElement) {
        document.head.removeChild(linkElement);
      }
    };
  }, [location]); // 每次路由變更時都會觸發

  return null; 
};

export default DynamicCSS;
