import api from "./api";

export interface Taxe {
  id: string;
  entreprise_id: number;
  nom: string;
  code: string;
  taux: number;
  description?: string;
  est_active: boolean;
  est_defaut: boolean;
}

export interface GroupeTaxe {
  id: string;
  entreprise_id: number;
  nom: string;
  description?: string;
  est_actif: boolean;
  taxes: Taxe[];
  taux_total: number;
}

export interface TaxeCreate {
  nom: string;
  code: string;
  taux: number;
  description?: string;
  est_active?: boolean;
  est_defaut?: boolean;
}

export interface GroupeTaxeCreate {
  nom: string;
  description?: string;
  taxe_ids: string[];
}

// ── Taxes ──────────────────────────────────────────────────
export const getTaxes = ()                          => api.get<Taxe[]>("/entreprises/taxes");
export const createTaxe = (data: TaxeCreate)        => api.post<Taxe>("/entreprises/taxes", data);
export const updateTaxe = (id: string, data: Partial<TaxeCreate>) => api.patch<Taxe>(`/entreprises/taxes/${id}`, data);
export const deleteTaxe = (id: string)              => api.delete(`/entreprises/taxes/${id}`);

// ── Groupes ────────────────────────────────────────────────
export const getGroupes = ()                                       => api.get<GroupeTaxe[]>("/entreprises/taxes/groupes");
export const createGroupe = (data: GroupeTaxeCreate)               => api.post<GroupeTaxe>("/entreprises/taxes/groupes", data);
export const updateGroupe = (id: string, data: Partial<GroupeTaxeCreate>) => api.patch<GroupeTaxe>(`/entreprises/taxes/groupes/${id}`, data);
export const deleteGroupe = (id: string)                           => api.delete(`/entreprises/taxes/groupes/${id}`);