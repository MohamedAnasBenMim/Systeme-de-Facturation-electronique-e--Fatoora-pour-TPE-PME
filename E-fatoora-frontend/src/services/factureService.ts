// services/factureService.ts
import api from "./api";

// Interfaces TypeScript
export interface Facture {
  id: number;
  client_id: number;
  entreprise_id: number;
  date_creation?: string;
  date_echeance: string;
  total_ht: number;
  total_tva: number;
  total_ttc: number;
  statut: 'brouillon' | 'payee' | 'envoyee';
  client?: { nom: string };
  lignes: Array<{
    produit_id: number;
    designation: string;
    quantite: number;
    prix_unitaire: number;
    montant_ligne: number;
  }>;
}

export interface FactureCreate {
  client_id: number;
  entreprise_id: number;
  date_echeance: string;
  lignes: Array<{
    produit_id: number;
    quantite: number;
    prix_unitaire: number;
  }>;
}

class FactureService {
  private basePath = '/factures';

  // ─── GET ALL ───
  async getAll(page: number = 1, pageSize: number = 10): Promise<Facture[]> {
    const response = await api.get(`${this.basePath}/`, { 
      params: { page, page_size: pageSize } 
    });
    return response.data || response;
  }

  // ─── GET ONE ───
  async getById(id: number): Promise<Facture> {
    const response = await api.get(`${this.basePath}/${id}`);
    return response.data || response;
  }

  // ─── GET DETAIL ───
  async getDetail(id: number): Promise<Facture> {
    const response = await api.get(`${this.basePath}/${id}/detail`);
    return response.data || response;
  }

  // ─── CREATE ───
  async create(facture: FactureCreate): Promise<Facture> {
  const response = await api.post(this.basePath, facture);
  return response.data || response;
 } 

// ─── UPDATE ───
 async update(id: number, facture: Partial<FactureCreate>): Promise<Facture> {
  const response = await api.put(`${this.basePath}/${id}`, facture);
  return response.data || response;
 }


  // ─── DELETE ───
  async delete(id: number): Promise<any> {
    const response = await api.delete(`${this.basePath}/${id}`);
    return response.data || response;
  }

  // ─── PDF ───
  async genererPdf(id: number): Promise<any> {
    const response = await api.post(`${this.basePath}/${id}/pdf`);
    return response.data || response;
  }

  async downloadPdf(id: number): Promise<Blob> {
  try {
    const response = await api.get(`${this.basePath}/${id}/pdf/download`, {
      responseType: 'blob',
      headers: {
        'Accept': 'application/pdf',
        'Cache-Control': 'no-cache'
      }
    });
    
    
    const contentType = response.headers['content-type'];
    if (!contentType?.includes('application/pdf')) {
      throw new Error(`Réponse non-PDF: ${contentType}`);
    }
    
    return response.data;
  } catch (error: any) {
    console.error("PDF Error details:", {
      status: error.response?.status,
      url: `${this.basePath}/${id}/pdf/download`,
      data: error.response?.data
    });
    throw error;
  }
}

  async previewPdf(id: number): Promise<Blob> {
    return api.get(`${this.basePath}/${id}/pdf/preview`, {
      responseType: 'blob'
    }).then(response => response.data);
  }
}

export default new FactureService();