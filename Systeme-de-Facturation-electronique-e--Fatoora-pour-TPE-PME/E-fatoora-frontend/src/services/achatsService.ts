import api from "./api";



export type StatutBonCommande = "BROUILLON" | "CONFIRMEE" | "LIVREE" | "DIFFERENCIEE";
export type StatutReception   = "PARTIELLE" | "COMPLETE" | "DIFFERENCIEE";
export type StatutBonRetour   = "BROUILLON" | "VALIDEE" | "TRAITEE";
export type StatutFacture     = "BROUILLON" | "EN_RAPPROCHEMENT" | "EN_LITIGE" | "VALIDEE" | "PAYEE";


export interface Fournisseur {
  id: number;
  nom: string;                        
  matricule_fiscal: string;           
  adresse: string;
  ville: string;
  code_postal?: string;
  telephone?: string;
  email?: string;
  contact_principal?: string;
  delai_paiement_jours: number;       
  escompte_pourcent: number;
  seuil_tolerance_quantite: number;
  seuil_tolerance_prix: number;
  actif: boolean;                    
  date_creation: string;
}

// ── Ligne Bon de Commande ────────────────────
export interface LigneBonCommande {
  id?: number;
  product_id: number;
  designation: string;                
  reference_fournisseur?: string;
  quantite_commandee: number;         
  quantite_receptionnee?: number;
  prix_unitaire: number;              
  montant_ligne: number;              
}

// ── Bon de Commande ──────────────────────────
export interface BonCommande {
  id: number;
  numero_bc: string;                  
  entreprise_id: number;
  fournisseur_id: number;
  fournisseur?: Fournisseur;
  statut: StatutBonCommande;          
  total_ht: number;
  tva: number;                       
  timbre_fiscal: number;
  total_ttc: number;
  date_creation: string;
  date_confirmation?: string;
  date_livraison_attendue?: string;   
  date_echeance_paiement?: string;
  confirmee: boolean;
  notes?: string;
  lignes: LigneBonCommande[];       
}

//Ligne Réception 
export interface LigneReception {
  id?: number;
  ligne_bc_id: number;
  quantite_receptionnee: number;
  quantite_conforme: number;
  quantite_non_conforme: number;
  conformite_acceptee: boolean;
  notes_conformite?: string;
}

// ── Réception ────────────────────────────────
export interface Reception {
  id: number;
  numero_reception: string;
  bon_commande_id: number;
  entreprise_id: number;
  fournisseur_id: number;
  statut: StatutReception;
  date_reception: string;
  numero_bl?: string;
  notes?: string;
  lignes: LigneReception[];
}

// ── Ligne Facture Fournisseur ────────────────
export interface LigneFacture {
  id?: number;
  ligne_bc_id?: number;
  product_id: number;
  designation: string;
  quantite_facturee: number;
  prix_unitaire: number;
  montant_ligne: number;
}

// ── Facture Fournisseur ──────────────────────
export interface FactureFournisseur {
  id: number;
  numero_facture: string;             // ← numero_facture
  bon_commande_id?: number;
  entreprise_id: number;
  fournisseur_id: number;
  fournisseur?: Fournisseur;
  statut: StatutFacture;
  total_ht: number;
  total_tva: number;
  total_ttc: number;
  total_ttc_net: number;              // ← total_ttc_net (après avoirs)
  date_facture: string;
  date_reception: string;
  date_echeance?: string;
  reference_bon_commande_fournisseur?: string;
  numero_bon_livraison_fournisseur?: string;
  notes?: string;
  lignes: LigneFacture[];
  litige?: LitigeFacture;
}

// ── Litige Facture ───────────────────────────
export interface LitigeFacture {
  id: number;
  facture_id: number;
  ecart_quantite: boolean;
  ecart_prix: boolean;
  ecart_montant: boolean;
  details_ecart: string;
  montant_litige: number;
  resolu: boolean;
  resolution?: string;
  date_detection: string;
  date_resolution?: string;
}

// ── Audit Trail ──────────────────────────────
export interface AuditEntry {
  id: number;
  action: string;
  ancien_statut?: string;
  nouveau_statut?: string;
  details_modification?: string;
  user_id?: number;
  date_action: string;
}

// ── Stats ────────────────────────────────────
export interface StatsGlobal {
  total_commandes: number;
  total_receptions: number;
  total_factures: number;
  montant_total_commandes: number;
  montant_total_factures: number;
  montant_total_paye: number;
  montant_total_restant: number;
  factures_en_retard: number;
  factures_en_litige: number;
}

export interface FournisseurFidele {
  fournisseur_id: number;
  nom: string;
  total_commandes: number;
  montant_total: number;
}

// ─────────────────────────────────────────────
// SERVICES
// ─────────────────────────────────────────────

export const fournisseurService = {
  getAll: (actifs_seulement = true): Promise<Fournisseur[]> =>
    api.get("/achats/fournisseurs", { params: { actifs_seulement } }).then(r => r.data),

  getById: (id: number): Promise<Fournisseur> =>
    api.get(`/achats/fournisseurs/${id}`).then(r => r.data),

  create: (data: Partial<Fournisseur>): Promise<Fournisseur> =>
    api.post("/achats/fournisseurs", data).then(r => r.data),

  update: (id: number, data: Partial<Fournisseur>): Promise<Fournisseur> =>
    api.put(`/achats/fournisseurs/${id}`, data).then(r => r.data),
};

export const bonCommandeService = {
  getAll: (entreprise_id?: number): Promise<BonCommande[]> =>
    api.get("/achats/bons-commande", { params: { entreprise_id } }).then(r => r.data),

  getById: (id: number): Promise<BonCommande> =>
    api.get(`/achats/bons-commande/${id}`).then(r => r.data),

  create: (data: Partial<BonCommande>): Promise<BonCommande> =>
    api.post("/achats/bons-commande", data).then(r => r.data),

  confirmer: (id: number): Promise<BonCommande> =>
    api.post(`/achats/bons-commande/${id}/confirmer`).then(r => r.data),
};

export const receptionService = {
  getById: (id: number): Promise<Reception> =>
    api.get(`/achats/receptions/${id}`).then(r => r.data),

  create: (data: Partial<Reception>): Promise<Reception> =>
    api.post("/achats/receptions", data).then(r => r.data),
};

export const factureAchatService = {
  getAll: (entreprise_id?: number): Promise<FactureFournisseur[]> =>
    api.get("/achats/factures-fournisseur", { params: { entreprise_id } }).then(r => r.data),

  getById: (id: number): Promise<FactureFournisseur> =>
    api.get(`/achats/factures-fournisseur/${id}`).then(r => r.data),

  create: (data: Partial<FactureFournisseur>): Promise<FactureFournisseur> =>
    api.post("/achats/factures-fournisseur", data).then(r => r.data),
};

export const litigeService = {
  getAll: (entreprise_id?: number): Promise<FactureFournisseur[]> =>
    api.get("/achats/litiges", { params: { entreprise_id } }).then(r => r.data),

  resoudre: (facture_id: number, data: { resolution: string }): Promise<any> =>
    api.post(`/achats/litiges/${facture_id}/resoudre`, data).then(r => r.data),
};

export const bonRetourService = {
  create: (data: any): Promise<any> =>
    api.post("/achats/bons-retour", data).then(r => r.data),

  valider: (id: number): Promise<any> =>
    api.post(`/achats/bons-retour/${id}/valider`).then(r => r.data),
};

export const statsAchatsService = {
  global: (entreprise_id: number, date_debut?: string, date_fin?: string): Promise<StatsGlobal> =>
    api.get("/achats/stats/global", { params: { entreprise_id, date_debut, date_fin } }).then(r => r.data),

  fournisseursFideles: (entreprise_id: number, limite = 5): Promise<FournisseurFidele[]> =>
    api.get("/achats/stats/fournisseurs-fideles", { params: { entreprise_id, limite } }).then(r => r.data),
};

export const auditService = {
  getBonCommande: (bc_id: number): Promise<AuditEntry[]> =>
    api.get(`/achats/audit-trail/bon-commande/${bc_id}`).then(r => r.data),

  getFacture: (facture_id: number): Promise<AuditEntry[]> =>
    api.get(`/achats/audit-trail/facture/${facture_id}`).then(r => r.data),
};