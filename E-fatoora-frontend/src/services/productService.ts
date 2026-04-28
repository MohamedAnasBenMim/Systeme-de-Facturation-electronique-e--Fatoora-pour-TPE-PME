import api from "./api";

export type TypeArticle = "PRODUIT" | "SERVICE";

export interface Categorie {
  id: number;
  nom: string;
  description?: string;
  parent_id?: number;
  sous_categories: Categorie[];
}

export interface UniteMesure {
  id: number;
  nom: string;
  code: string;
}

export interface Produit {
  id: number;
  entreprise_id: number;
  type: TypeArticle;
  designation: string;
  reference?: string;
  code_barre?: string;
  description?: string;
  image_url?: string;
  marque?: string;
  prix_achat_ht: number;
  prix_vente_ht: number;
  prix_vente_ttc?: number;
  taxe_id?: string;
  groupe_taxe_id?: string;
  is_stockable: boolean;
  est_actif: boolean;
  categorie?: Categorie;
  unite?: UniteMesure;
  date_creation: string;
}

export interface ProduitCreate {
  type: TypeArticle;
  designation: string;
  reference?: string;
  code_barre?: string;
  description?: string;
  marque?: string;
  categorie_id?: number;
  unite_id?: number;
  prix_achat_ht: number;
  prix_vente_ht: number;
  taxe_id?: string;
  groupe_taxe_id?: string;
  is_stockable: boolean;
}

export interface ProduitListResponse {
  items: Produit[];
  total: number;
  page: number;
  pages: number;
}

export interface SearchParams {
  q?: string;
  type?: TypeArticle;
  categorie_id?: number;
  est_actif?: boolean;
  page?: number;
  limit?: number;
}

// ── Produits ───────────────────────────────────────────
export const getProduits = (params: SearchParams = {}) =>
  api.get<ProduitListResponse>("/produits", { params });

export const getProduit = (id: number) =>
  api.get<Produit>(`/produits/${id}`);

export const createProduit = (data: ProduitCreate) =>
  api.post<Produit>("/produits", data);

export const updateProduit = (id: number, data: Partial<ProduitCreate>) =>
  api.patch<Produit>(`/produits/${id}`, data);

export const deleteProduit = (id: number) =>
  api.delete(`/produits/${id}`);

export const uploadImage = (id: number, file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post<Produit>(`/produits/${id}/image`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// ── Catégories ─────────────────────────────────────────
export const getCategories = () =>
  api.get<Categorie[]>("/produits/categories");

export const createCategorie = (data: { nom: string; description?: string; parent_id?: number }) =>
  api.post<Categorie>("/produits/categories", data);

export const deleteCategorie = (id: number) =>
  api.delete(`/produits/categories/${id}`);

// ── Unités ─────────────────────────────────────────────
export const getUnites = () =>
  api.get<UniteMesure[]>("/produits/unites");

export const createUnite = (data: { nom: string; code: string }) =>
  api.post<UniteMesure>("/produits/unites", data);

// ── Bulk ───────────────────────────────────────────────
export const bulkUpdatePrix = (data: {
  categorie_id?: number;
  pourcentage: number;
  type_prix: "vente" | "achat";
}) => api.patch("/produits/bulk/prix", data);

// ── Import / Export ────────────────────────────────────
export const importCSV = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/produits/import", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const exportCSV = () =>
  api.get("/produits/export", { responseType: "blob" });