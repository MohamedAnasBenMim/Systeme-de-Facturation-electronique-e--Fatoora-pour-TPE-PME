import axios from "axios";

// instance axios configurée
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1", // URL de ton API Gateway
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