// src/services/ventesService.ts
import api from "./api";

// ── TYPES ─────────────────────────────────────────────────────

export type StatutDevis = "BROUILLON" | "ENVOYE" | "ACCEPTE" | "REFUSE" | "EXPIRE" | "CONVERTI";
export type StatutBC    = "BROUILLON" | "CONFIRME" | "EN_COURS" | "LIVRE" | "FACTURE" | "ANNULE";
export type StatutBL    = "EN_ATTENTE" | "EN_COURS" | "LIVRE" | "PARTIEL" | "ANNULE" | "FACTURE";

export interface LigneVente {
  produit_id: number;
  description: string;
  quantite: number;
  prix_unitaire: number;
  taux_tva: number;
  montant_ht: number;
}

export interface Devis {
  id: number;
  numero: string;
  client_id: number;
  statut: StatutDevis;
  date_creation: string;
  date_expiration?: string;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  notes?: string;
  type_conversion?: string;
  lignes: LigneVente[];
}

export interface BonCommande {
  id: number;
  numero: string;
  client_id: number;
  devis_id?: number;
  statut: StatutBC;
  date_creation: string;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  notes?: string;
  lignes: LigneVente[];
}

export interface BonLivraison {
  id: number;
  numero: string;
  client_id: number;
  bc_id?: number;
  devis_id?: number;
  source: string;
  statut: StatutBL;
  date_creation: string;
  date_livraison?: string;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  facture_id_externe?: number;
  lignes: LigneVente[];
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

// ── DEVIS ─────────────────────────────────────────────────────

export const devisService = {
  getAll: ()                => api.get<Devis[]>("/devis/").then(r => r.data),
  getById: (id: number)     => api.get<Devis>(`/devis/${id}`).then(r => r.data),
  create: (payload: object) => api.post<Devis>("/devis/", payload).then(r => r.data),
  delete: (id: number)      => api.delete(`/devis/${id}`).then(r => r.data),

  envoyer:  (id: number) => api.put<Devis>(`/devis/${id}/envoyer`).then(r => r.data),
  accepter: (id: number) => api.put<Devis>(`/devis/${id}/accepter`).then(r => r.data),
  refuser:  (id: number) => api.put<Devis>(`/devis/${id}/refuser`).then(r => r.data),

  convertirEnBC:      (id: number) => api.post(`/devis/${id}/convertir/bon-commande`).then(r => r.data),
  convertirEnBL:      (id: number) => api.post(`/devis/${id}/convertir/bon-livraison`).then(r => r.data),
  convertirEnFacture: (id: number) => api.post(`/devis/${id}/convertir/facture`).then(r => r.data),

  generatePdf: (id: number) => api.get(`/devis/${id}/pdf`, { responseType: 'blob' }).then(r => r.data),
};

// ── BON DE COMMANDE ───────────────────────────────────────────

export const bonCommandeService = {
  getAll: (page = 1, pageSize = 10) =>
    api.get<PaginatedResponse<BonCommande>>("/bon-commande/", { params: { page, page_size: pageSize } }).then(r => r.data),
  getById: (id: number) =>
    api.get<BonCommande>(`/bon-commande/${id}`).then(r => r.data),
  createManuel: (payload: object) =>
    api.post<BonCommande>("/bon-commande/manuel", payload).then(r => r.data),

  changerStatut: (id: number, statut: string) =>
    api.put<BonCommande>(`/bon-commande/${id}/statut`, null, { params: { statut } }).then(r => r.data),

  convertirEnBL:      (id: number) => api.post(`/bon-commande/${id}/convertir/bon-livraison`).then(r => r.data),
  convertirEnFacture: (id: number) => api.post(`/bon-commande/${id}/convertir/facture`).then(r => r.data),

  generatePdf: (id: number) => api.get(`/bon-commande/${id}/pdf`, { responseType: 'blob' }).then(r => r.data),
};

// ── BON DE LIVRAISON ─────────────────────────────────────────
export const bonLivraisonService = {
  create: (payload: object) => api.post<BonLivraison>("/bon-livraison/", payload).then(r => r.data),
  getAll: (page = 1, pageSize = 10) =>
    api.get<PaginatedResponse<BonLivraison>>("/bon-livraison/", { params: { page, page_size: pageSize } }).then(r => r.data),
  getById: (id: number) =>
    api.get<BonLivraison>(`/bon-livraison/${id}`).then(r => r.data),
  delete: (id: number) =>
    api.delete(`/bon-livraison/${id}`),

  confirmer:  (id: number) => api.put<BonLivraison>(`/bon-livraison/${id}/confirmer`).then(r => r.data),
  annuler:    (id: number) => api.put<BonLivraison>(`/bon-livraison/${id}/annuler`).then(r => r.data),
  creerPartiel: (id: number) => api.post<BonLivraison>(`/bon-livraison/${id}/partiel`).then(r => r.data),

  convertirEnFacture:       (id: number)        => api.post(`/bon-livraison/${id}/convertir/facture`).then(r => r.data),
  convertirGroupeEnFacture: (blIds: number[])   => api.post(`/bon-livraison/convertir/facture-groupee`, blIds).then(r => r.data),

  generatePdf: (id: number) => api.get(`/bon-livraison/${id}/pdf`, { responseType: 'blob' }).then(r => r.data),
};