import { useState, useEffect, useCallback, useMemo } from "react";
import api from "../../../services/api";

// ── Types ──────────────────────────────────────────────────────

interface Client {
  id: number;
  nom: string;
  prenom?: string;
  email?: string;
  adresse?: string;
  matricule_fiscal?: string;
}

interface Entreprise {
  id: number;
  nom: string;
  adresse?: string;
  telephone?: string;
  email?: string;
  logo_url?: string;
  matricule_fiscal?: string;
  rib?: string;
}

interface Produit {
  id: number;
  designation: string;
  prix_unitaire: number;
  prix_vente?: number;
  prix_vente_ht?: number;
  taux_tva?: number;
  stock_disponible?: number;
  source_catalogue?: "STOCK" | "E_FATOORA";
}

export interface LigneDocument {
  product_id: number;
  designation: string;
  quantite: number;
  prix_unitaire: number;
  taux_tva: number;
  remise: number;
  montant_ht: number;
}

export interface DocumentFormData {
  client_id: number;
  entreprise_id: number;
  date_document: string;
  date_echeance?: string;
  notes: string;
  lignes: LigneDocument[];
}

interface DocumentFormProps {
  titre: string;
  sousTitre?: string;
  numeroApercu: string;
  showEcheance?: boolean;
  labelEcheance?: string;
  submitLabel?: string;
  onSubmit: (data: DocumentFormData) => Promise<void>;
  onCancel: () => void;
}

// ── Helpers ────────────────────────────────────────────────────

const formatCurrency = (val: number) =>
  val.toLocaleString("fr-TN", { minimumFractionDigits: 3, maximumFractionDigits: 3 }) + " DT";

const todayStr = () => new Date().toISOString().split("T")[0];
const nextMonthStr = () => {
  const d = new Date();
  d.setMonth(d.getMonth() + 1);
  return d.toISOString().split("T")[0];
};

const toArray = <T,>(payload: any): T[] => {
  if (Array.isArray(payload)) return payload;
  return payload?.items ?? payload?.data ?? payload?.results ?? payload?.clients ?? [];
};

const normalizePrix = (produit: Produit) =>
  Number(produit.prix_unitaire ?? produit.prix_vente ?? produit.prix_vente_ht ?? 0);

const calcTotaux = (lignes: LigneDocument[]) => {
  const total_ht  = Math.round(lignes.reduce((s, l) => s + l.montant_ht, 0) * 1000) / 1000;
  const total_tva = Math.round(
    lignes.reduce((s, l) => s + l.montant_ht * (l.taux_tva / 100), 0) * 1000
  ) / 1000;
  const timbre_fiscal = 1.0;
  const total_ttc = Math.round((total_ht + total_tva + timbre_fiscal) * 1000) / 1000;
  return { total_ht, total_tva, timbre_fiscal, total_ttc };
};

function IconPlus() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
    </svg>
  );
}
function IconTrash() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  );
}
function IconCheck() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
    </svg>
  );
}
function IconArrowLeft() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
  );
}
function IconEye() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );
}

// ── Modal aperçu ───────────────────────────────────────────────

function PreviewModal({
  open, onClose, titre, numeroApercu, entreprise, client, lignes, totaux, dateDoc, dateEcheance,
}: {
  open: boolean; onClose: () => void; titre: string; numeroApercu: string;
  entreprise: Entreprise | null; client: Client | null;
  lignes: LigneDocument[]; totaux: ReturnType<typeof calcTotaux>;
  dateDoc: string; dateEcheance: string;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-white w-full max-w-[210mm] max-h-[95vh] overflow-auto shadow-2xl">
        <div className="p-8 min-h-[297mm]">
          {/* En-tête entreprise */}
          <div className="flex items-start justify-between mb-8">
            <div className="flex-1">
              <p className="text-lg font-bold text-gray-900">{entreprise?.nom ?? "—"}</p>
              <p className="text-sm text-gray-500 mt-1">{entreprise?.adresse ?? ""}</p>
              <p className="text-sm text-gray-500">{entreprise?.telephone ?? ""}</p>
              <p className="text-sm text-gray-500">{entreprise?.email ?? ""}</p>
              {entreprise?.matricule_fiscal && <p className="text-xs text-gray-400 mt-1">MF : {entreprise.matricule_fiscal}</p>}
              {entreprise?.rib && <p className="text-xs text-gray-400">RIB : {entreprise.rib}</p>}
            </div>
            <div className="w-28 h-20 border border-gray-200 flex items-center justify-center overflow-hidden bg-white rounded-md">
              {entreprise?.logo_url
                ? <img src={entreprise.logo_url} alt="Logo" className="w-full h-full object-contain" />
                : <span className="text-xs text-gray-400">LOGO</span>
              }
            </div>
          </div>

          {/* Titre document */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b-2 border-slate-900">
            <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">{titre.toUpperCase()}</h1>
              <p className="text-sm text-slate-500 font-mono mt-0.5">N° {numeroApercu}</p>
            </div>
          </div>

          {/* Client + Dates */}
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Destinataire</p>
              {client ? (
                <>
                  <p className="font-bold text-slate-900">
                    {`${client.prenom ?? ""} ${client.nom ?? ""}`.trim() || `Client #${client.id}`}
                  </p>
                  <p className="text-sm text-slate-500">{client.email ?? ""}</p>
                  <p className="text-sm text-slate-500">{client.adresse ?? ""}</p>
                  {client.matricule_fiscal && <p className="text-xs text-slate-400 mt-1">MF : {client.matricule_fiscal}</p>}
                </>
              ) : (
                <p className="text-slate-400 italic">Aucun client sélectionné</p>
              )}
            </div>
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Dates</p>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Date</span>
                  <span className="font-medium text-slate-800">{dateDoc}</span>
                </div>
                {dateEcheance && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Échéance</span>
                    <span className="font-medium text-slate-800">{dateEcheance}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Tableau lignes */}
          <table className="w-full mb-8 text-sm border border-gray-200 border-collapse">
            <thead>
              <tr className="bg-slate-900 text-white">
                <th className="px-4 py-3 text-left font-semibold">Désignation</th>
                <th className="px-4 py-3 text-center font-semibold">Qté</th>
                <th className="px-4 py-3 text-right font-semibold">Prix unit.</th>
                <th className="px-4 py-3 text-center font-semibold">Remise</th>
                <th className="px-4 py-3 text-center font-semibold">TVA</th>
                <th className="px-4 py-3 text-right font-semibold">Montant HT</th>
              </tr>
            </thead>
            <tbody>
              {lignes.length === 0
                ? <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-400 italic">Aucune ligne</td></tr>
                : lignes.map((l, i) => (
                    <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                      <td className="px-4 py-3 text-slate-800">{l.designation}</td>
                      <td className="px-4 py-3 text-center text-slate-600">{l.quantite}</td>
                      <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(l.prix_unitaire)}</td>
                      <td className="px-4 py-3 text-center text-slate-500">{l.remise > 0 ? `${l.remise}%` : "—"}</td>
                      <td className="px-4 py-3 text-center text-slate-500">{l.taux_tva}%</td>
                      <td className="px-4 py-3 text-right font-medium text-slate-900">{formatCurrency(l.montant_ht)}</td>
                    </tr>
                  ))
              }
            </tbody>
          </table>

          {/* Totaux */}
          <div className="flex justify-end">
            <div className="w-72 space-y-2">
              {[
                { label: "Total HT",       val: totaux.total_ht },
                { label: "Total TVA",      val: totaux.total_tva },
                { label: "Timbre Fiscal",  val: totaux.timbre_fiscal },
              ].map(({ label, val }) => (
                <div key={label} className="flex justify-between text-sm py-1 border-b border-slate-100">
                  <span className="text-slate-500">{label}</span>
                  <span className="font-medium text-slate-800">{formatCurrency(val)}</span>
                </div>
              ))}
              <div className="flex justify-between items-center py-3 bg-slate-900 text-white px-4 mt-2">
                <span className="font-bold">Total TTC</span>
                <span className="text-xl font-black">{formatCurrency(totaux.total_ttc)}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="sticky bottom-0 bg-white border-t border-slate-100 px-8 py-4 flex justify-end">
          <button onClick={onClose} className="px-6 py-2.5 bg-slate-900 text-white font-semibold text-sm">
            Fermer l'aperçu
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Composant principal ────────────────────────────────────────

export function DocumentForm({
  titre, sousTitre, numeroApercu, showEcheance = false, labelEcheance = "Date d'échéance",
  submitLabel = "Enregistrer", onSubmit, onCancel,
}: DocumentFormProps) {
  const [entreprise, setEntreprise]           = useState<Entreprise | null>(null);
  const [clients, setClients]                 = useState<Client[]>([]);
  const [produits, setProduits]               = useState<Produit[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | "">("");
  const [lignes, setLignes]                   = useState<LigneDocument[]>([]);
  const [dateDoc, setDateDoc]                 = useState(todayStr());
  const [dateEcheance, setDateEcheance]       = useState(nextMonthStr());
  const [notes, setNotes]                     = useState("");
  const [previewOpen, setPreviewOpen]         = useState(false);
  const [loading, setLoading]                 = useState(false);
  const [dataLoading, setDataLoading]         = useState(true);
  const [toast, setToast]                     = useState<{ msg: string; type: "success" | "error" } | null>(null);

  const selectedClient = useMemo(
    () => clients.find(c => c.id === Number(selectedClientId)) ?? null,
    [clients, selectedClientId]
  );
  const totaux = useMemo(() => calcTotaux(lignes), [lignes]);

  // Chargement des données (clients, produits stock, entreprise)
  useEffect(() => {
    const load = async () => {
      setDataLoading(true);
      try {
        const [clientsRes, stockProduitsRes, stockLevelsRes, produitsRes, entrepriseRes] = await Promise.allSettled([
          api.get("/clients/"),
          api.get("/stock/produits"),
          api.get("/stock/stocks"),
          api.get("/produits/"),
          api.get("/entreprises/mon-profil"),
        ]);
        if (clientsRes.status === "fulfilled") setClients(toArray<Client>(clientsRes.value.data));
        const stockProducts = stockProduitsRes.status === "fulfilled"
          ? toArray<Produit>(stockProduitsRes.value.data)
          : [];
        const stockLevels = stockLevelsRes.status === "fulfilled"
          ? toArray<any>(stockLevelsRes.value.data)
          : [];

        if (stockProducts.length > 0) {
          const quantites = stockLevels.reduce<Record<number, number>>((acc, stock) => {
            const productId = Number(stock.produit_id);
            acc[productId] = (acc[productId] ?? 0) + Number(stock.quantite ?? 0);
            return acc;
          }, {});
          setProduits(stockProducts.map((p) => ({
            ...p,
            prix_unitaire: normalizePrix(p),
            stock_disponible: quantites[Number(p.id)] ?? 0,
            source_catalogue: "STOCK",
          })));
        } else if (produitsRes.status === "fulfilled") {
          setProduits(toArray<Produit>(produitsRes.value.data).map((p) => ({
            ...p,
            prix_unitaire: normalizePrix(p),
            source_catalogue: "E_FATOORA",
          })));
        }
        if (entrepriseRes.status === "fulfilled") setEntreprise(entrepriseRes.value.data ?? null);
      } finally { setDataLoading(false); }
    };
    load();
  }, []);

  useEffect(() => {
    if (toast) { const t = setTimeout(() => setToast(null), 3500); return () => clearTimeout(t); }
  }, [toast]);

  // Gestion des lignes
  const addLigne = useCallback(() => {
    setLignes(prev => [...prev, { product_id: 0, designation: "", quantite: 1, prix_unitaire: 0, taux_tva: 19, remise: 0, montant_ht: 0 }]);
  }, []);

  const removeLigne = useCallback((idx: number) => {
    setLignes(prev => prev.filter((_, i) => i !== idx));
  }, []);

  const updateLigneProduit = useCallback((idx: number, produit_id: number) => {
    const p = produits.find(p => p.id === produit_id);
    if (!p) return;
    setLignes(prev => prev.map((l, i) => i !== idx ? l : {
      ...l,
      product_id: p.id,
      designation: p.designation,
      prix_unitaire: normalizePrix(p),
      taux_tva: p.taux_tva ?? 19,
      montant_ht: Math.round(l.quantite * normalizePrix(p) * (1 - l.remise / 100) * 1000) / 1000,
    }));
  }, [produits]);

  const updateLigneField = useCallback((idx: number, field: keyof LigneDocument, val: number) => {
    setLignes(prev => prev.map((l, i) => {
      if (i !== idx) return l;
      const updated = { ...l, [field]: val };
      updated.montant_ht = Math.round(updated.quantite * updated.prix_unitaire * (1 - updated.remise / 100) * 1000) / 1000;
      return updated;
    }));
  }, []);

  const validate = () => {
    if (!selectedClientId) { setToast({ msg: "Veuillez sélectionner un client.", type: "error" }); return false; }
    if (!entreprise)        { setToast({ msg: "Aucune entreprise trouvée.",        type: "error" }); return false; }
    if (lignes.length === 0) { setToast({ msg: "Ajoutez au moins une ligne.",       type: "error" }); return false; }
    if (lignes.some(l => !l.product_id)) { setToast({ msg: "Chaque ligne doit avoir un produit.", type: "error" }); return false; }
    const ligneStockInsuffisant = lignes.find((l) => {
      const produit = produits.find((p) => p.id === l.product_id);
      return produit?.source_catalogue === "STOCK"
        && produit.stock_disponible !== undefined
        && l.quantite > produit.stock_disponible;
    });
    if (ligneStockInsuffisant) {
      const produit = produits.find((p) => p.id === ligneStockInsuffisant.product_id);
      setToast({
        msg: `Stock insuffisant pour ${produit?.designation ?? "ce produit"}. Disponible : ${produit?.stock_disponible ?? 0}.`,
        type: "error",
      });
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await onSubmit({
        client_id: Number(selectedClientId),
        entreprise_id: entreprise!.id,
        date_document: dateDoc,
        date_echeance: showEcheance ? dateEcheance : undefined,
        notes,
        lignes,
      });
      setToast({ msg: "Document créé avec succès !", type: "success" });
    } catch (e: any) {
      setToast({ msg: e.response?.data?.detail || "Erreur lors de la création.", type: "error" });
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl text-sm font-medium transition-all ${
          toast.type === "success" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
        }`}>
          {toast.type === "success" ? <IconCheck /> : "✕"} {toast.msg}
        </div>
      )}

      {/* Modal aperçu */}
      <PreviewModal
        open={previewOpen} onClose={() => setPreviewOpen(false)}
        titre={titre} numeroApercu={numeroApercu}
        entreprise={entreprise} client={selectedClient}
        lignes={lignes} totaux={totaux}
        dateDoc={dateDoc} dateEcheance={dateEcheance}
      />

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* En-tête */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button onClick={onCancel}
              className="flex items-center gap-2 text-slate-500 hover:text-slate-900 text-sm font-medium transition-colors">
              <IconArrowLeft /> Retour
            </button>
            <div className="w-px h-5 bg-slate-300" />
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">{titre}</h1>
              <p className="text-xs font-mono text-slate-400 mt-0.5">{numeroApercu}</p>
            </div>
          </div>
        </div>

        {dataLoading ? (
          <div className="flex items-center justify-center py-32 text-slate-400">
            Chargement des données...
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Colonne principale */}
            <div className="lg:col-span-2 space-y-6">

              {/* Entreprise + Client */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">
                  {/* Entreprise */}
                  <div className="p-6">
                    {entreprise ? (
                      <div className="flex items-start gap-4">
                        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center border border-slate-200 shrink-0 overflow-hidden">
                          {entreprise.logo_url
                            ? <img src={entreprise.logo_url} alt="Logo" className="w-full h-full object-contain" />
                            : <span className="text-[10px] text-slate-400 font-bold">LOGO</span>
                          }
                        </div>
                        <div>
                          <p className="font-bold text-slate-900">{entreprise.nom}</p>
                          <p className="text-xs text-slate-400 mt-1">{entreprise.adresse ?? ""}</p>
                          <p className="text-xs text-slate-400">{entreprise.telephone ?? ""}</p>
                          <p className="text-xs text-slate-400 font-mono mt-1">MF : {entreprise.matricule_fiscal ?? "—"}</p>
                          <p className="text-xs text-slate-400 font-mono">RIB : {entreprise.rib ?? "—"}</p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-slate-400">Aucune entreprise trouvée.</p>
                    )}
                  </div>

                  {/* Client */}
                  <div className="p-6">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Client</p>
                    <div className="relative">
                      <select value={selectedClientId}
                        onChange={e => setSelectedClientId(e.target.value === "" ? "" : Number(e.target.value))}
                        className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 pr-10 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition">
                        <option value="">Sélectionner un client…</option>
                        {clients.map(c => (
                          <option key={c.id} value={c.id}>
                            {`${c.prenom ?? ""} ${c.nom ?? ""}`.trim() || `Client #${c.id}`} — {c.email ?? ""}
                          </option>
                        ))}
                      </select>
                      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </span>
                    </div>
                    {selectedClient && (
                      <div className="mt-3 bg-slate-50 rounded-xl p-3 text-xs text-slate-500 space-y-0.5">
                        <p className="font-semibold text-slate-700">
                          {`${selectedClient.prenom ?? ""} ${selectedClient.nom ?? ""}`.trim()}
                        </p>
                        <p>{selectedClient.email ?? ""}</p>
                        <p>{selectedClient.adresse ?? ""}</p>
                        {selectedClient.matricule_fiscal && <p>MF : {selectedClient.matricule_fiscal}</p>}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Dates */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">
                      Date du document
                    </label>
                    <input type="date" value={dateDoc} onChange={e => setDateDoc(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition" />
                  </div>
                  {showEcheance && (
                    <div>
                      <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">
                        {labelEcheance}
                      </label>
                      <input type="date" value={dateEcheance} onChange={e => setDateEcheance(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition" />
                    </div>
                  )}
                </div>
              </div>

              {/* Lignes */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="px-6 pt-5 pb-3 flex items-center justify-between border-b border-slate-100">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Lignes</p>
                  <button onClick={addLigne}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-700 transition">
                    <IconPlus /> Ajouter une ligne
                  </button>
                </div>

                {/* En-tête colonnes */}
                <div className="grid grid-cols-12 gap-2 px-6 py-2.5 bg-slate-50 text-xs font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100">
                  <div className="col-span-4">Désignation</div>
                  <div className="col-span-1 text-center">Qté</div>
                  <div className="col-span-2 text-right">Prix HT</div>
                  <div className="col-span-1 text-right">Remise</div>
                  <div className="col-span-1 text-center">TVA</div>
                  <div className="col-span-2 text-right">Montant HT</div>
                  <div className="col-span-1" />
                </div>

                {/* Lignes */}
                <div className="divide-y divide-slate-50">
                  {lignes.length === 0 ? (
                    <div className="px-6 py-10 text-center">
                      <p className="text-slate-400 text-sm">Aucune ligne — cliquez sur « Ajouter une ligne »</p>
                    </div>
                  ) : (
                    lignes.map((ligne, idx) => (
                      <div key={idx} className="grid grid-cols-12 gap-2 px-6 py-3 items-center hover:bg-slate-50/60 transition-colors">
                        {/* Produit */}
                        <div className="col-span-4">
                          <select value={ligne.product_id || ""}
                            onChange={e => updateLigneProduit(idx, Number(e.target.value))}
                            className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition">
                            <option value="">Choisir un produit…</option>
                            {produits.map(p => (
                              <option key={p.id} value={p.id}>
                                {p.designation}
                                {p.source_catalogue === "STOCK" ? ` — Stock: ${p.stock_disponible ?? 0}` : ""}
                              </option>
                            ))}
                          </select>
                        </div>
                        {/* Quantité */}
                        <div className="col-span-1">
                          <input type="number" min={1} value={ligne.quantite}
                            onChange={e => updateLigneField(idx, "quantite", Math.max(1, Number(e.target.value)))}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-slate-900 transition" />
                        </div>
                        {/* Prix unitaire */}
                        <div className="col-span-2">
                          <input type="number" min={0} step={0.001} value={ligne.prix_unitaire}
                            onChange={e => updateLigneField(idx, "prix_unitaire", Math.max(0, Number(e.target.value)))}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-sm text-right focus:outline-none focus:ring-2 focus:ring-slate-900 transition" />
                        </div>
                        {/* Remise */}
                        <div className="col-span-1">
                          <div className="flex items-center bg-slate-50 border border-slate-200 rounded-lg px-2 py-2">
                            <input type="number" min={0} max={100} value={ligne.remise}
                              onChange={e => updateLigneField(idx, "remise", Math.min(100, Math.max(0, Number(e.target.value))))}
                              className="w-full text-sm text-right bg-transparent focus:outline-none" />
                            <span className="text-xs text-slate-400 ml-1">%</span>
                          </div>
                        </div>
                        {/* TVA */}
                        <div className="col-span-1">
                          <select value={ligne.taux_tva}
                            onChange={e => updateLigneField(idx, "taux_tva", Number(e.target.value))}
                            className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 transition">
                            <option value={0}>0%</option>
                            <option value={7}>7%</option>
                            <option value={13}>13%</option>
                            <option value={19}>19%</option>
                          </select>
                        </div>
                        {/* Montant HT */}
                        <div className="col-span-2 text-right text-sm font-semibold text-slate-700">
                          {ligne.montant_ht.toFixed(3)}
                        </div>
                        {/* Supprimer */}
                        <div className="col-span-1 flex justify-end">
                          <button onClick={() => removeLigne(idx)}
                            className="w-8 h-8 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 flex items-center justify-center transition">
                            <IconTrash />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Notes */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-3">
                  Notes / Conditions
                </label>
                <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3}
                  placeholder="Conditions de paiement, délais, remarques..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition resize-none placeholder-slate-300" />
              </div>
            </div>

            {/* Colonne droite */}
            <div className="space-y-4">
              {/* Récapitulatif */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Récapitulatif</p>
                <div className="space-y-3">
                  {[
                    { label: "Total HT",      val: totaux.total_ht },
                    { label: "Total TVA",     val: totaux.total_tva },
                    { label: "Timbre Fiscal", val: totaux.timbre_fiscal },
                  ].map(({ label, val }) => (
                    <div key={label} className="flex justify-between items-center text-sm border-b border-slate-100 pb-2">
                      <span className="text-slate-500">{label}</span>
                      <span className="font-semibold text-slate-800 tabular-nums">{formatCurrency(val)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center pt-2">
                    <span className="font-bold text-slate-900">Total TTC</span>
                    <span className="text-xl font-black text-slate-900 tabular-nums">{formatCurrency(totaux.total_ttc)}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-3">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Actions</p>
                <button onClick={() => setPreviewOpen(true)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-slate-200 text-slate-700 rounded-xl text-sm font-semibold hover:border-slate-900 hover:text-slate-900 transition">
                  <IconEye /> Aperçu
                </button>
                <button onClick={handleSubmit} disabled={loading}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-700 transition disabled:opacity-60 shadow-md shadow-slate-200">
                  {loading ? "Création..." : <><IconCheck /> {submitLabel}</>}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
