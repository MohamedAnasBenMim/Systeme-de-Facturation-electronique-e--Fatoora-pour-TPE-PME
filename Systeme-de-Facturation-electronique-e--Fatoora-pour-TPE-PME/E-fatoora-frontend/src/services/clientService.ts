import api from "./api";

// 🔹 récupérer tous les clients (avec pagination)
export const getClients = async (skip = 0, limit = 100) => {
  const response = await api.get("/clients/", {
    params: { skip, limit },
  });
  return response.data;
};

// 🔹 récupérer un client par id
export const getClientById = async (id: number) => {
  const response = await api.get(`/clients/${id}`);
  return response.data;
};

// 🔹 récupérer client par email
export const getClientByEmail = async (email: string) => {
  const response = await api.get(`/clients/email/${email}`);
  return response.data;
};

// 🔹 créer client
export const createClient = async (data: any) => {
  const response = await api.post("/clients", data);
  return response.data;
};

// 🔹 update client
export const updateClient = async (id: number, data: any) => {
  const response = await api.put(`/clients/${id}`, data);
  return response.data;
};

// 🔹 delete client
export const deleteClient = async (id: number) => {
  await api.delete(`/clients/${id}`);
};