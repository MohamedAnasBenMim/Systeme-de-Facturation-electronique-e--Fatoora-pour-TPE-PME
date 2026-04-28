import { useState, useEffect, useCallback, useMemo } from "react";
import api from "../../services/api";
import factureService from "../../services/factureService";

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
}

interface LigneFacture {
  product_id: number;
  designation: string;
  quantite: number;
  prix_unitaire: number;
  montant_ligne: number;
}

type StatutFacture = "BROUILLON" | "ENVOYEE" | "PAYEE" | "ANNULEE";

const formatCurrency = (val: number) =>
  val.toLocaleString("fr-TN", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }) + " DT";

const calcTotaux = (lignes: LigneFacture[]) => {
  const total_ht = lignes.reduce((s, l) => s + l.montant_ligne, 0);
  const tva = Math.round(total_ht * 0.19 * 1000) / 1000;
  const timbre_fiscal = 1.0;
  const total_ttc = Math.round((total_ht + tva + timbre_fiscal) * 1000) / 1000;
  return {
    total_ht: Math.round(total_ht * 1000) / 1000,
    tva,
    timbre_fiscal,
    total_ttc,
  };
};

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

function StatusBadge({ statut }: { statut: StatutFacture }) {
  const map: Record<StatutFacture, { label: string; cls: string }> = {
    BROUILLON: { label: "Brouillon", cls: "bg-amber-100 text-amber-700 border-amber-200" },
    ENVOYEE: { label: "Envoyée", cls: "bg-blue-100 text-blue-700 border-blue-200" },
    PAYEE: { label: "Payée", cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
    ANNULEE: { label: "Annulée", cls: "bg-red-100 text-red-700 border-red-200" },
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${map[statut].cls}`}>
      {map[statut].label}
    </span>
  );
}

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

function IconEye() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );
}

function IconMail() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
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

function PreviewModal({
  open,
  onClose,
  entreprise,
  client,
  lignes,
  totaux,
  dateEcheance,
  factureNo,
  statut,
}: {
  open: boolean;
  onClose: () => void;
  entreprise: Entreprise | null;
  client: Client | null;
  lignes: LigneFacture[];
  totaux: ReturnType<typeof calcTotaux>;
  dateEcheance: string;
  factureNo: string;
  statut: StatutFacture;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-white w-full max-w-[210mm] max-h-[95vh] overflow-auto shadow-2xl">
        <div className="p-8 min-h-[297mm]">
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
              {entreprise?.logo_url ? (
                <img src={entreprise.logo_url} alt="Logo entreprise" className="w-full h-full object-contain" />
              ) : (
                <span className="text-xs text-gray-400">LOGO</span>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between mb-6 pb-4 border-b-2 border-slate-900">
            <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">FACTURE</h1>
              <p className="text-sm text-slate-500 font-mono mt-0.5">N° {factureNo || "——"}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Facturé à</p>
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
                  <span className="text-slate-500">Émission</span>
                  <span className="font-medium text-slate-800">{todayStr()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Échéance</span>
                  <span className="font-medium text-slate-800">{dateEcheance || "—"}</span>
                </div>
              </div>
            </div>
          </div>

          <table className="w-full mb-8 text-sm border border-gray-200 border-collapse">
            <thead>
              <tr className="bg-slate-900 text-white">
                <th className="px-4 py-3 text-left font-semibold">Désignation</th>
                <th className="px-4 py-3 text-center font-semibold">Qté</th>
                <th className="px-4 py-3 text-right font-semibold">Prix unit.</th>
                <th className="px-4 py-3 text-right font-semibold">Montant HT</th>
              </tr>
            </thead>
            <tbody>
              {lignes.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-slate-400 italic">
                    Aucune ligne
                  </td>
                </tr>
              ) : (
                lignes.map((l, i) => (
                  <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                    <td className="px-4 py-3 text-slate-800">{l.designation}</td>
                    <td className="px-4 py-3 text-center text-slate-600">{l.quantite}</td>
                    <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(l.prix_unitaire)}</td>
                    <td className="px-4 py-3 text-right font-medium text-slate-900">{formatCurrency(l.montant_ligne)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          <div className="flex justify-end">
            <div className="w-72 space-y-2">
              {[
                { label: "Total Net HTVA", val: totaux.total_ht },
                { label: "Total TVA (19%)", val: totaux.tva },
                { label: "Timbre Fiscal", val: totaux.timbre_fiscal },
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
            Fermer l’aperçu
          </button>
        </div>
      </div>
    </div>
  );
}

export default function FacturePage() {
  const [entreprise, setEntreprise] = useState<Entreprise | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [produits, setProduits] = useState<Produit[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | "">("");
  const [selectedEntrepriseId, setSelectedEntrepriseId] = useState<number | "">("");
  const [lignes, setLignes] = useState<LigneFacture[]>([]);
  const [dateEcheance, setDateEcheance] = useState<string>(nextMonthStr());
  const [statut, setStatut] = useState<StatutFacture>("BROUILLON");
  const [previewOpen, setPreviewOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: "success" | "error" } | null>(null);
  const [factureNo] = useState<string>(
    `FAC-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9000) + 1000)}`
  );

  const selectedClient = useMemo(
    () => clients.find((c) => c.id === Number(selectedClientId)) ?? null,
    [clients, selectedClientId]
  );

  const selectedEntreprise = useMemo(() => entreprise, [entreprise]);
  const totaux = useMemo(() => calcTotaux(lignes), [lignes]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        try {
          const clientsRes = await api.get("/clients/");
          setClients(toArray<Client>(clientsRes.data));
        } catch (error) {
          console.error("Erreur clients:", error);
          setClients([]);
        }

        try {
          const produitsRes = await api.get("/products/");
          setProduits(toArray<Produit>(produitsRes.data));
        } catch (error) {
          console.error("Erreur produits:", error);
          setProduits([]);
        }

        try {
          const entrepriseRes = await api.get("/entreprises/mon-profil");
          setEntreprise(entrepriseRes.data ?? null);
          setSelectedEntrepriseId(entrepriseRes.data?.id ?? "");
        } catch (error) {
          console.error("Erreur entreprise:", error);
          setEntreprise(null);
          setSelectedEntrepriseId("");
        }
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const addLigne = useCallback(() => {
    setLignes((prev) => [
      ...prev,
      { product_id: 0, designation: "", quantite: 1, prix_unitaire: 0, montant_ligne: 0 },
    ]);
  }, []);

  const removeLigne = useCallback((idx: number) => {
    setLignes((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  const updateLigneProduit = useCallback(
    (idx: number, produit_id: number) => {
    const produit = produits.find((p) => p.id=== produit_id);
      if (!produit) return;

      setLignes((prev) =>
        prev.map((l, i) =>
          i === idx
            ? {
                ...l,
                product_id: produit.id,
                designation: produit.designation,
                prix_unitaire: produit.prix_unitaire,
                montant_ligne: Math.round(l.quantite * produit.prix_unitaire * 1000) / 1000,
              }
            : l
        )
      );
    },
    [produits]
  );

  const updateLigneQuantite = useCallback((idx: number, val: number) => {
    setLignes((prev) =>
      prev.map((l, i) =>
        i === idx ? { ...l, quantite: val, montant_ligne: Math.round(val * l.prix_unitaire * 1000) / 1000 } : l
      )
    );
  }, []);

  const updateLignePrix = useCallback((idx: number, val: number) => {
    setLignes((prev) =>
      prev.map((l, i) =>
        i === idx ? { ...l, prix_unitaire: val, montant_ligne: Math.round(l.quantite * val * 1000) / 1000 } : l
      )
    );
  }, []);

  const validate = () => {
    if (!selectedClientId) {
      setToast({ msg: "Veuillez sélectionner un client.", type: "error" });
      return false;
    }
    if (!selectedEntreprise) {
      setToast({ msg: "Veuillez charger une entreprise.", type: "error" });
      return false;
    }
    if (lignes.length === 0) {
      setToast({ msg: "Ajoutez au moins une ligne.", type: "error" });
      return false;
    }
    if (lignes.some((l) => !l.product_id)) {
      setToast({ msg: "Chaque ligne doit avoir un produit.", type: "error" });
      return false;
    }
    return true;
  };

  const handleCreate = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      const payload = {
        client_id: Number(selectedClientId),
        entreprise_id: Number(selectedEntrepriseId),
        date_echeance: dateEcheance || null,
        lignes: lignes.map((l) => ({
          product_id: l.product_id,
          quantite: l.quantite,
          prix_unitaire: l.prix_unitaire,
        })),
      };

      await factureService.create(payload);
      setToast({ msg: "Facture créée avec succès !", type: "success" });
      setTimeout(() => {
        window.location.href = "/factures";
      }, 1200);
    } catch (error) {
      console.error(error);
      setToast({ msg: "Erreur lors de la création.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!validate()) return;
    if (!selectedClient?.email) {
      setToast({ msg: "Ce client n'a pas d'e-mail.", type: "error" });
      return;
    }
    setLoading(true);
    try {
      setToast({ msg: `Facture prête à être envoyée à ${selectedClient.email}`, type: "success" });
    } catch (error) {
      setToast({ msg: "Erreur lors de l'envoi.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-[system-ui]">
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl text-sm font-medium transition-all duration-300 ${
            toast.type === "success" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
          }`}
        >
          {toast.type === "success" ? <IconCheck /> : "✕"}
          {toast.msg}
        </div>
      )}

      <PreviewModal
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        entreprise={selectedEntreprise}
        client={selectedClient}
        lignes={lignes}
        totaux={totaux}
        dateEcheance={dateEcheance}
        factureNo={factureNo}
        statut={statut}
      />

      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => (window.location.href = "/invoices")}
              className="flex items-center gap-2 text-slate-500 hover:text-slate-900 text-sm font-medium transition-colors"
            >
              <IconArrowLeft /> Retour
            </button>
            <div className="w-px h-5 bg-slate-300" />
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">Nouvelle Facture</h1>
              <p className="text-xs font-mono text-slate-400 mt-0.5">{factureNo}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">
                <div className="p-6">
                  {selectedEntreprise ? (
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center border border-slate-200 shrink-0 overflow-hidden">
                        {selectedEntreprise.logo_url ? (
                          <img
                            src={selectedEntreprise.logo_url}
                            alt="Logo entreprise"
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <span className="text-[10px] text-slate-400 font-bold">LOGO</span>
                        )}
                      </div>
                      <div>
                        <p className="font-bold text-slate-900">{selectedEntreprise.nom}</p>
                        <p className="text-xs text-slate-400 mt-1">{selectedEntreprise.adresse ?? ""}</p>
                        <p className="text-xs text-slate-400">{selectedEntreprise.telephone ?? ""}</p>
                        <p className="text-xs text-slate-400 font-mono mt-1">
                          MF : {selectedEntreprise.matricule_fiscal ?? "—"}
                        </p>
                        <p className="text-xs text-slate-400 font-mono">RIB : {selectedEntreprise.rib ?? "—"}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400">Aucune entreprise trouvée.</p>
                  )}
                </div>

                <div className="p-6">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Client</p>
                  <div className="flex items-center gap-2">
                    <div className="relative flex-1">
                      <select
                        value={selectedClientId}
                        onChange={(e) => setSelectedClientId(e.target.value === "" ? "" : Number(e.target.value))}
                        className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 pr-10 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition"
                      >
                        <option value="">Sélectionner un client…</option>
                        {clients.length === 0 ? (
                          <option value="" disabled>
                            Aucun client disponible
                          </option>
                        ) : (
                          clients.map((c) => (
                            <option key={c.id} value={c.id}>
                              {`${c.prenom ?? ""} ${c.nom ?? ""}`.trim() || `Client #${c.id}`}
                            </option>
                          ))
                        )}
                      </select>
                      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </span>
                    </div>
                    <button
                      title="Nouveau client"
                      onClick={() => {}}
                      className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center hover:bg-slate-700 transition shrink-0"
                    >
                      <IconPlus />
                    </button>
                  </div>

                  {selectedClient && (
                    <div className="mt-3 bg-slate-50 rounded-xl p-3 text-xs text-slate-500 space-y-0.5">
                      <p>{`${selectedClient.prenom ?? ""} ${selectedClient.nom ?? ""}`.trim() || `Client #${selectedClient.id}`}</p>
                      <p>{selectedClient.email ?? ""}</p>
                      <p>{selectedClient.adresse ?? ""}</p>
                      {selectedClient.matricule_fiscal && <p>MF : {selectedClient.matricule_fiscal}</p>}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">
                    Date d'échéance
                  </label>
                  <input
                    type="date"
                    value={dateEcheance}
                    onChange={(e) => setDateEcheance(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition"
                  />
                </div>
                
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="px-6 pt-5 pb-3 flex items-center justify-between border-b border-slate-100">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Lignes de facture</p>
                <button
                  onClick={addLigne}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-700 transition"
                >
                  <IconPlus /> Ajouter une ligne
                </button>
              </div>

              <div className="grid grid-cols-12 gap-2 px-6 py-2.5 bg-slate-50 text-xs font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100">
                <div className="col-span-5">Désignation</div>
                <div className="col-span-2 text-center">Quantité</div>
                <div className="col-span-3 text-right">Prix unit. (DT)</div>
                <div className="col-span-1 text-right">Montant</div>
                <div className="col-span-1" />
              </div>

              <div className="divide-y divide-slate-50">
                {lignes.length === 0 ? (
                  <div className="px-6 py-10 text-center">
                    <p className="text-slate-400 text-sm">Aucune ligne — cliquez sur « Ajouter »</p>
                  </div>
                ) : (
                  lignes.map((ligne, idx) => (
                    <div key={idx} className="grid grid-cols-12 gap-2 px-6 py-3 items-center hover:bg-slate-50/60 transition-colors">
                      <div className="col-span-5">
                        <select
                          value={ligne.product_id || ""}
                          onChange={(e) => updateLigneProduit(idx, Number(e.target.value))}
                          className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition"
                        >
                          <option value="">Choisir un produit…</option>
                          {produits.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.designation}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="col-span-2">
                        <input
                          type="number"
                          min={1}
                          value={ligne.quantite}
                          onChange={(e) => updateLigneQuantite(idx, Math.max(1, Number(e.target.value) || 1))}
                          className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-center text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition"
                        />
                      </div>

                      <div className="col-span-3">
                        <input
                          type="number"
                          min={0}
                          step={0.001}
                          value={ligne.prix_unitaire}
                          onChange={(e) => updateLignePrix(idx, Math.max(0, Number(e.target.value) || 0))}
                          className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-right text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 transition"
                        />
                      </div>

                      <div className="col-span-1 text-right text-sm font-semibold text-slate-700">
                        {ligne.montant_ligne.toFixed(3)}
                      </div>

                      <div className="col-span-1 flex justify-end">
                        <button
                          onClick={() => removeLigne(idx)}
                          className="w-8 h-8 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 flex items-center justify-center transition"
                        >
                          <IconTrash />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Récapitulatif</p>
              <div className="space-y-3">
                {[
                  { label: "Total Net HTVA", val: totaux.total_ht },
                  { label: "Total TVA (19%)", val: totaux.tva },
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

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-3">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Actions</p>

              <button
                onClick={() => setPreviewOpen(true)}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-slate-200 text-slate-700 rounded-xl text-sm font-semibold hover:border-slate-900 hover:text-slate-900 transition"
              >
                <IconEye /> Aperçu 
              </button>

              <button
                onClick={handleSendEmail}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-blue-200 text-blue-700 rounded-xl text-sm font-semibold hover:border-blue-600 hover:text-blue-800 transition disabled:opacity-50"
              >
                <IconMail /> Envoyer par e-mail
              </button>

              <button
                onClick={handleCreate}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 px-4 py-3.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-700 transition disabled:opacity-60 shadow-md shadow-slate-200"
              >
                {loading ? "Création…" : (
                  <>
                    <IconCheck /> Créer la facture
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}