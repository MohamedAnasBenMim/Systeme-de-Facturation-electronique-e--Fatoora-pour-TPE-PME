import api from "./api";

export const login = async (email: string, password: string) => {
  const response = await api.post("/auth/login", { email, password });
  const { access_token } = response.data;
  localStorage.setItem("token", access_token); // stocké pour l'interceptor
  window.location.href = "/dashboard"; 
  return response.data;
};

export const logout = () => {
  localStorage.removeItem("token");
};

export const isAuthenticated = () => {
  return !!localStorage.getItem("token");
};