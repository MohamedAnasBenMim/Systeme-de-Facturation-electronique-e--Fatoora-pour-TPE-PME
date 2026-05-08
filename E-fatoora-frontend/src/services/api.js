import axios from "axios";

// instance axios configurée
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:9000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor pour ajouter automatiquement le token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // ou sessionStorage

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
