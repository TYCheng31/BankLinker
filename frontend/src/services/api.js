import axios from "axios";

export const api = axios.create({
  baseURL: import.meta?.env?.VITE_API_BASE || process.env.REACT_APP_API_BASE || "http://192.168.1.61:8000",
});

export function setAuthToken(token) {
  if (token) api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  else delete api.defaults.headers.common["Authorization"];
}
