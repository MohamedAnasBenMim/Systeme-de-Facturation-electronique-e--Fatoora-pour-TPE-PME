import { useEffect, useState, useMemo } from "react";
import api from "../../services/api";
import factureService from "../../services/factureService";

interface LigneFactureResponse {
  id: number;
  product_id: number;
  designation: string;
  quantite: number;
  prix_unitaire: number;
  montant_ligne: number;
}

interface FactureResponse {
  id: number;
  client_id: number;
  entreprise_id: number;
  total_ht: number;
  tva: number;
  timbre_fiscal: number;
  total_ttc: number;
  date_creation: string;
  date_echeance: string | null;
  statut: StatutFacture;
  pdf_path: string | null;
  lignes: LigneFactureResponse[];
}

interface Client {
  id: number;
  nom: string;
  prenom?: string;
  email?: string;
  adresse?: string;
  matricule_fiscal?: string;
}

type StatutFacture = "BROUILLON" | "ENVOYEE" | "PAYEE" | "ANNULEE";

const formatCurrency = (val: number) =>
  val.toLocaleString("fr-TN", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }) + " DT";

const formatDate = (d: string | null) =>
  d ? new Date(d).toLocaleDateString("fr-FR") : "—";

// ✅ FIX : extraction robuste qui couvre toutes les structures possibles
const extractArray = <T,>(data: any, fallbackKeys: string[] = []): T[] => {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  // Cherche dans les clés connues + fallbackKeys
  for (const key of ["items", "data", "results", "factures", "clients", ...fallbackKeys]) {
    if (Array.isArray(data[key])) return data[key];
  }
  console.warn("⚠️ Structure API inattendue :", data);
  return [];
};

const STATUT_MAP: Record<StatutFacture, { label: string; cls: string }> = {
  BROUILLON: { label: "Brouillon", cls: "bg-amber-100 text-amber-700 border-amber-200" },
  ENVOYEE:   { label: "Envoyée",   cls: "bg-blue-100 text-blue-700 border-blue-200" },
  PAYEE:     { label: "Payée",     cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  ANNULEE:   { label: "Annulée",   cls: "bg-red-100 text-red-700 border-red-200" },
};

function StatusBadge({ statut }: { statut: string }) {
  // ✅ FIX : accepte n'importe quelle string, pas seulement StatutFacture
  const s = STATUT_MAP[statut as StatutFacture] ?? {
    label: statut,
    cls: "bg-gray-100 text-gray-600 border-gray-200",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>
      {s.label}
    </span>
  );
}

function DetailModal({
  facture,
  client,
  onClose,
  onChangeStatut,
  onDownloadPdf,
}: {
  facture: FactureResponse;
  client: Client | null;
  onClose: () => void;
  onChangeStatut: (id: number, statut: StatutFacture) => Promise<void>;
  onDownloadPdf: (id: number) => Promise<void>;
}) {
  const [loadingStatut, setLoadingStatut] = useState(false);

  const handleStatut = async (statut: StatutFacture) => {
    setLoadingStatut(true);
    await onChangeStatut(facture.id, statut);
    setLoadingStatut(false);
  };

  const actions: { label: string; statut: StatutFacture; cls: string }[] = [];
  if (facture.statut === "BROUILLON") {
    actions.push({ label: "Marquer Envoyée", statut: "ENVOYEE", cls: "border-blue-200 text-blue-700 hover:bg-blue-50" });
    actions.push({ label: "Annuler",         statut: "ANNULEE", cls: "border-red-200 text-red-600 hover:bg-red-50" });
  }
  if (facture.statut === "ENVOYEE") {
    actions.push({ label: "Marquer Payée",   statut: "PAYEE",   cls: "border-emerald-200 text-emerald-700 hover:bg-emerald-50" });
    actions.push({ label: "Annuler",         statut: "ANNULEE", cls: "border-red-200 text-red-600 hover:bg-red-50" });
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Facture #{facture.id}</h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">Créée le {formatDate(facture.date_creation)}</p>
          </div>
          <StatusBadge statut={facture.statut} />
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Client</p>
              {client ? (
                <>
                  <p className="font-semibold text-slate-800">
                    {`${client.prenom ?? ""} ${client.nom ?? ""}`.trim() || `Client #${client.id}`}
                  </p>
                  {/* ✅ Email affiché */}
                  <p className="text-sm text-blue-600">{client.email ?? "—"}</p>
                  <p className="text-sm text-slate-500">{client.adresse ?? ""}</p>
                  {client.matricule_fiscal && (
                    <p className="text-xs text-slate-400 mt-1">MF : {client.matricule_fiscal}</p>
                  )}
                </>
              ) : (
                <p className="text-slate-400 italic text-sm">Client #{facture.client_id}</p>
              )}
            </div>

            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Dates</p>
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Création</span>
                  <span className="font-medium text-slate-800">{formatDate(facture.date_creation)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Échéance</span>
                  <span className="font-medium text-slate-800">{formatDate(facture.date_echeance)}</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Lignes</p>
            <table className="w-full text-sm border border-slate-100 rounded-xl overflow-hidden">
              <thead className="bg-slate-900 text-white">
                <tr>
                  <th className="px-4 py-2.5 text-left font-semibold">Désignation</th>
                  <th className="px-4 py-2.5 text-center font-semibold">Qté</th>
                  <th className="px-4 py-2.5 text-right font-semibold">Prix unit.</th>
                  <th className="px-4 py-2.5 text-right font-semibold">Montant HT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {facture.lignes.map((l, i) => (
                  <tr key={l.id} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                    <td className="px-4 py-2.5 text-slate-800">{l.designation}</td>
                    <td className="px-4 py-2.5 text-center text-slate-600">{l.quantite}</td>
                    <td className="px-4 py-2.5 text-right text-slate-600">{formatCurrency(l.prix_unitaire)}</td>
                    <td className="px-4 py-2.5 text-right font-semibold text-slate-900">{formatCurrency(l.montant_ligne)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-end">
            <div className="w-72 space-y-2">
              {[
                { label: "Total HT",      val: facture.total_ht },
                { label: "TVA (19%)",     val: facture.tva },
                { label: "Timbre Fiscal", val: facture.timbre_fiscal },
              ].map(({ label, val }) => (
                <div key={label} className="flex justify-between text-sm py-1 border-b border-slate-100">
                  <span className="text-slate-500">{label}</span>
                  <span className="font-medium text-slate-800">{formatCurrency(val)}</span>
                </div>
              ))}
              <div className="flex justify-between items-center py-3 bg-slate-900 text-white px-4 mt-2 rounded-xl">
                <span className="font-bold text-sm">Total TTC</span>
                <span className="text-lg font-black">{formatCurrency(facture.total_ttc)}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
            <button
              onClick={() => onDownloadPdf(facture.id)}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 transition"
            >
              📄 Télécharger PDF
            </button>
            {actions.map((a) => (
              <button
                key={a.statut}
                onClick={() => handleStatut(a.statut)}
                disabled={loadingStatut}
                className={`px-4 py-2 text-sm font-semibold border rounded-xl transition disabled:opacity-50 ${a.cls}`}
              >
                {a.label}
              </button>
            ))}
            <button
              onClick={onClose}
              className="ml-auto px-4 py-2 text-sm font-semibold border border-slate-200 text-slate-500 rounded-xl hover:bg-slate-50 transition"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FacturesListPage() {
  const [factures, setFactures]               = useState<FactureResponse[]>([]);
  const [clientMap, setClientMap]             = useState<Record<number, Client>>({});
  const [loading, setLoading]                 = useState(true);
  const [selectedFacture, setSelectedFacture] = useState<FactureResponse | null>(null);
  const [filterStatut, setFilterStatut]       = useState<StatutFacture | "TOUS">("TOUS");
  const [page, setPage]                       = useState(1);
  const [toast, setToast]                     = useState<{ msg: string; type: "success" | "error" } | null>(null);
  const PAGE_SIZE = 10;

  const showToast = (msg: string, type: "success" | "error") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [facturesRes, clientsRes] = await Promise.all([
        api.get("/factures/"),
        api.get("/clients/"),
      ]);

      // ✅ FIX PRINCIPAL : log pour voir la vraie structure et extraction correcte
      console.log("📦 Factures API response:", facturesRes.data);
      console.log("👥 Clients API response:", clientsRes.data);

      const facturesList: FactureResponse[] = extractArray(facturesRes.data, ["factures"]);
      const clientsList: Client[]           = extractArray(clientsRes.data, ["clients"]);

      console.log(`✅ ${facturesList.length} factures extraites`);
      console.log(`✅ ${clientsList.length} clients extraits`);

      // ✅ Vérifie les statuts réels reçus
      const statuts = [...new Set(facturesList.map(f => f.statut))];
      console.log("📊 Statuts présents dans les factures:", statuts);

      const map: Record<number, Client> = {};
      clientsList.forEach((c) => { map[c.id] = c; });

      setFactures(facturesList);
      setClientMap(map);
    } catch (err) {
      console.error("❌ Erreur fetchAll:", err);
      showToast("Erreur lors du chargement des factures.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleChangeStatut = async (id: number, statut: StatutFacture) => {
    try {
      await factureService.updateStatut(id, statut);
      showToast("Statut mis à jour.", "success");
      await fetchAll();
      setSelectedFacture((prev) =>
        prev?.id === id ? { ...prev, statut } : prev
      );
    } catch (err: any) {
      showToast(err.response?.data?.detail || "Erreur lors du changement de statut.", "error");
    }
  };

  const handleDownloadPdf = async (id: number) => {
    try {
      const blob = await factureService.generatePdf(id);
      const url  = window.URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `facture_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch {
      showToast("Erreur lors du téléchargement du PDF.", "error");
    }
  };

  const filtered = useMemo(() =>
    filterStatut === "TOUS"
      ? factures
      : factures.filter((f) => f.statut === filterStatut),
    [factures, filterStatut]
  );

  const paginated  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  const stats = useMemo(() => ({
    total:     factures.length,
    brouillon: factures.filter((f) => f.statut === "BROUILLON").length,
    envoyee:   factures.filter((f) => f.statut === "ENVOYEE").length,
    payee:     factures.filter((f) => f.statut === "PAYEE").length,
    annulee:   factures.filter((f) => f.statut === "ANNULEE").length,
    ca:        factures.filter((f) => f.statut === "PAYEE")
                       .reduce((s, f) => s + f.total_ttc, 0),
  }), [factures]);

  return (
    <div className="min-h-screen bg-slate-50 font-[system-ui]">
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl text-sm font-medium transition-all ${
          toast.type === "success" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
        }`}>
          {toast.type === "success" ? "✓" : "✕"} {toast.msg}
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">Factures</h1>
            <p className="text-slate-400 text-sm mt-1">Gérez et suivez toutes vos factures</p>
          </div>
          <button
            onClick={() => window.location.href = "/factures/nouvelle"}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-700 transition shadow-md"
          >
            + Nouvelle facture
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "Total",      val: stats.total,     color: "text-slate-900" },
            { label: "Brouillons", val: stats.brouillon, color: "text-amber-600" },
            { label: "Envoyées",   val: stats.envoyee,   color: "text-blue-600" },
            { label: "Payées",     val: stats.payee,     color: "text-emerald-600" },
            { label: "Annulées",   val: stats.annulee,   color: "text-red-500" },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
              <p className={`text-2xl font-black ${s.color}`}>{s.val}</p>
              <p className="text-xs font-medium text-slate-400 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl px-6 py-4 flex items-center justify-between">
          <p className="text-sm font-semibold text-emerald-700">Chiffre d'affaires encaissé</p>
          <p className="text-2xl font-black text-emerald-700">{formatCurrency(stats.ca)}</p>
        </div>

        <div className="flex flex-wrap gap-2">
          {(["TOUS", "BROUILLON", "ENVOYEE", "PAYEE", "ANNULEE"] as const).map((s) => (
            <button
              key={s}
              onClick={() => { setFilterStatut(s); setPage(1); }}
              className={`px-4 py-1.5 rounded-full text-xs font-bold border transition ${
                filterStatut === s
                  ? "bg-slate-900 text-white border-slate-900"
                  : "bg-white text-slate-500 border-slate-200 hover:border-slate-900 hover:text-slate-900"
              }`}
            >
              {s === "TOUS" ? "Toutes" : STATUT_MAP[s].label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="bg-white rounded-2xl border border-slate-200 py-20 text-center text-slate-400">
            Chargement…
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white rounded-2xl border-2 border-dashed border-slate-200 py-20 text-center">
            <p className="text-slate-400 text-sm">Aucune facture trouvée.</p>
            <button
              onClick={() => window.location.href = "/factures/nouvelle"}
              className="mt-4 px-5 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-700 transition"
            >
              + Créer une facture
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {["ID", "Client", "Statut", "Total HT", "TVA", "Timbre", "Total TTC", "Création", "Échéance", "Actions"].map((h) => (
                    <th
                      key={h}
                      className={`px-4 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider ${
                        ["Total HT","TVA","Timbre","Total TTC"].includes(h) ? "text-right" :
                        h === "Actions" ? "text-center" : "text-left"
                      }`}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {paginated.map((f) => {
                  const client = clientMap[f.client_id] ?? null;
                  return (
                    <tr key={f.id} className="hover:bg-slate-50/60 transition">
                      <td className="px-4 py-3.5 font-mono font-semibold text-blue-600 text-xs">
                        #{f.id}
                      </td>

                      {/* ✅ Client : nom + email */}
                      <td className="px-4 py-3.5">
                        {client ? (
                          <div>
                            <p className="font-semibold text-slate-800 text-xs">
                              {`${client.prenom ?? ""} ${client.nom ?? ""}`.trim()}
                            </p>
                            <p className="text-blue-500 text-xs">{client.email ?? "—"}</p>
                          </div>
                        ) : (
                          <span className="text-slate-400 italic text-xs">Client #{f.client_id}</span>
                        )}
                      </td>

                      {/* ✅ Statut réel depuis la BDD — pas de valeur par défaut */}
                      <td className="px-4 py-3.5">
                        <StatusBadge statut={f.statut} />
                      </td>

                      <td className="px-4 py-3.5 text-right text-slate-700 font-medium tabular-nums text-xs">
                        {formatCurrency(f.total_ht)}
                      </td>
                      <td className="px-4 py-3.5 text-right text-slate-500 tabular-nums text-xs">
                        {formatCurrency(f.tva)}
                      </td>
                      <td className="px-4 py-3.5 text-right text-slate-500 tabular-nums text-xs">
                        {formatCurrency(f.timbre_fiscal)}
                      </td>
                      <td className="px-4 py-3.5 text-right font-bold text-slate-900 tabular-nums text-xs">
                        {formatCurrency(f.total_ttc)}
                      </td>

                      <td className="px-4 py-3.5 text-slate-400 text-xs">
                        {formatDate(f.date_creation)}
                      </td>
                      <td className="px-4 py-3.5 text-xs">
                        {f.date_echeance ? (
                          <span className={
                            new Date(f.date_echeance) < new Date() && f.statut !== "PAYEE"
                              ? "text-red-500 font-semibold"
                              : "text-slate-400"
                          }>
                            {formatDate(f.date_echeance)}
                          </span>
                        ) : "—"}
                      </td>

                      <td className="px-4 py-3.5">
                        <div className="flex items-center justify-center gap-1.5">
                          <button
                            onClick={() => setSelectedFacture(f)}
                            className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:border-slate-900 hover:text-slate-900 transition"
                          >
                            Voir
                          </button>
                          <button
                            onClick={() => handleDownloadPdf(f.id)}
                            className="px-3 py-1.5 text-xs font-semibold border border-blue-200 text-blue-600 rounded-lg hover:bg-blue-50 transition"
                          >
                            PDF
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">{filtered.length} facture(s)</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="w-8 h-8 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-40 transition text-xs font-bold"
                  >
                    ‹
                  </button>
                  <span className="text-xs text-slate-600 font-medium">
                    Page {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="w-8 h-8 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-40 transition text-xs font-bold"
                  >
                    ›
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {selectedFacture && (
        <DetailModal
          facture={selectedFacture}
          client={clientMap[selectedFacture.client_id] ?? null}
          onClose={() => setSelectedFacture(null)}
          onChangeStatut={handleChangeStatut}
          onDownloadPdf={handleDownloadPdf}
        />
      )}
    </div>
  );
}