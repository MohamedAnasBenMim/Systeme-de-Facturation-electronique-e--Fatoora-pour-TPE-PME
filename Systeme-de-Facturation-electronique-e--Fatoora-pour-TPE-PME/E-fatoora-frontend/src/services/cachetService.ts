import api from "./api";

export interface Cachet {
  id: string;
  entreprise_id: number;
  nom?: string;
  image_mime: string;
  created_at: string;
  updated_at: string;
}

export const getCachet    = ()                              => api.get<Cachet>("/entreprises/cachet");
export const getCachetImageUrl = ()                         => `${import.meta.env.VITE_API_URL}/entreprises/cachet/image`;
export const uploadCachet = (file: File, nom?: string) => {
  const form = new FormData();
  form.append("file", file);
  if (nom) form.append("nom", nom);
  return api.post<{ message: string; cachet: Cachet }>("/entreprises/cachet", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
export const deleteCachet = () => api.delete("/entreprises/cachet");