import { useEffect, useState, useMemo } from "react";
import { useSearchParams } from "react-router";
import {
  Plus, Download, ChevronLeft, ChevronRight,
  FileText, CheckCircle, XCircle, Send, Eye,
  CalendarDays,
} from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { DocumentForm, type DocumentFormData } from "../components/ventes/DocumentForm";
import api from "../../services/api";
import factureService from "../../services/factureService";

// ─── Types ───────────────────────────────────────────────────────────────────

interface LigneFactureResponse {
  id: number;
  product_id: number;
  designation: string;
  quantite: number;
  prix_unitaire: number;
  taux_tva?: number;
  remise?: number;
  montant_ht?: number;
  montant_ligne: number;
}

interface FactureResponse {
  id: number;
  numero?: string;
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

type StatutFacture = "BROUILLON" | "VALIDEE" | "PAYEE" | "ANNULEE";

// ─── Constants ────────────────────────────────────────────────────────────────

const STATUT_MAP: Record<string, { label: string; cls: string }> = {
  BROUILLON: { label: "Brouillon", cls: "bg-amber-100 text-amber-700 border-amber-200" },
  VALIDEE:   { label: "Validée",   cls: "bg-blue-100 text-blue-700 border-blue-200" },
  PAYEE:     { label: "Payée",     cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  ANNULEE:   { label: "Annulée",   cls: "bg-red-100 text-red-700 border-red-200" },
};

const MONTH_FR = [
  "Janvier","Février","Mars","Avril","Mai","Juin",
  "Juillet","Août","Septembre","Octobre","Novembre","Décembre",
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

const formatCurrency = (val: number) =>
  val.toLocaleString("fr-TN", { minimumFractionDigits: 3, maximumFractionDigits: 3 }) + " DT";

const formatDate = (d: string | null) =>
  d ? new Date(d).toLocaleDateString("fr-FR") : "—";

const extractArray = <T,>(data: any, fallbackKeys: string[] = []): T[] => {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  for (const key of ["items", "data", "results", "factures", "clients", ...fallbackKeys]) {
    if (Array.isArray(data[key])) return data[key];
  }
  return [];
};

// Groups factures by "Month Year" then by "DD/MM/YYYY"
const groupByMonthAndDay = (factures: FactureResponse[]) => {
  const byMonth: Record<string, Record<string, FactureResponse[]>> = {};
  const sorted = [...factures].sort(
    (a, b) => new Date(b.date_creation).getTime() - new Date(a.date_creation).getTime()
  );
  sorted.forEach((f) => {
    const d = new Date(f.date_creation);
    const monthKey = `${MONTH_FR[d.getMonth()]} ${d.getFullYear()}`;
    const dayKey   = d.toLocaleDateString("fr-FR");
    if (!byMonth[monthKey]) byMonth[monthKey] = {};
    if (!byMonth[monthKey][dayKey]) byMonth[monthKey][dayKey] = [];
    byMonth[monthKey][dayKey].push(f);
  });
  return byMonth;
};

// ─── StatusBadge ─────────────────────────────────────────────────────────────

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUT_MAP[statut] ?? { label: statut, cls: "bg-gray-100 text-gray-600 border-gray-200" };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>
      {s.label}
    </span>
  );
}

// ─── DetailModal ─────────────────────────────────────────────────────────────

function DetailModal({
  facture, client, onClose, onChangeStatut, onDownloadPdf,
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
    actions.push({ label: "Marquer Validée", statut: "VALIDEE", cls: "border-blue-200 text-blue-700 hover:bg-blue-50" });
    actions.push({ label: "Annuler",         statut: "ANNULEE", cls: "border-red-200 text-red-600 hover:bg-red-50" });
  }
  if (facture.statut === "VALIDEE") {
    actions.push({ label: "Marquer Payée",   statut: "PAYEE",   cls: "border-emerald-200 text-emerald-700 hover:bg-emerald-50" });
    actions.push({ label: "Annuler",         statut: "ANNULEE", cls: "border-red-200 text-red-600 hover:bg-red-50" });
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-lg">
              {facture.numero ?? `Facture #${facture.id}`}
            </h3>
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
                  <span className={`font-medium ${
                    facture.date_echeance && new Date(facture.date_echeance) < new Date() && facture.statut !== "PAYEE"
                      ? "text-red-500"
                      : "text-slate-800"
                  }`}>
                    {formatDate(facture.date_echeance)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Lignes */}
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

          {/* Totaux */}
          <div className="flex justify-end">
            <div className="w-72 space-y-2">
              {[
                { label: "Total HT",      val: facture.total_ht },
                { label: "TVA",           val: facture.tva },
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

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
            <button
              onClick={() => onDownloadPdf(facture.id)}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 transition"
            >
              <Download className="w-3.5 h-3.5" /> PDF
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

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function FacturesListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [factures, setFactures]               = useState<FactureResponse[]>([]);
  const [clientMap, setClientMap]             = useState<Record<number, Client>>({});
  const [loading, setLoading]                 = useState(true);
  const [showForm, setShowForm]               = useState(false);
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
      const facturesList: FactureResponse[] = extractArray(facturesRes.data, ["factures"]);
      const clientsList: Client[]           = extractArray(clientsRes.data, ["clients"]);
      const map: Record<number, Client> = {};
      clientsList.forEach((c) => { map[c.id] = c; });
      setFactures(facturesList);
      setClientMap(map);
    } catch {
      showToast("Erreur lors du chargement des factures.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  useEffect(() => {
    if (searchParams.get("new") === "1") {
      setShowForm(true);
    }
  }, [searchParams]);

  // ── Create facture from form ───────────────────────────────────────────────
  const handleCreate = async (data: DocumentFormData) => {
    try {
      const lignes = (data.lignes || [])
        .map((l) => ({
          product_id: Number(l.product_id),
          quantite: Number(l.quantite),
          prix_unitaire: Number(l.prix_unitaire),
        }))
        .filter((l) => Number.isFinite(l.product_id) && l.product_id > 0
          && Number.isFinite(l.quantite) && l.quantite > 0
          && Number.isFinite(l.prix_unitaire) && l.prix_unitaire > 0);

      if (lignes.length === 0) {
        showToast("Ajoute au moins une ligne valide (produit, quantité, prix).", "error");
        return;
      }

      await api.post("/factures/", {
        client_id:     Number(data.client_id),
        entreprise_id: 1,
        date_echeance: data.date_echeance || null,
        lignes,
      });
      showToast("Facture créée avec succès.", "success");
      setShowForm(false);
      setSearchParams({});
      fetchAll();
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Erreur lors de la création.", "error");
    }
  };

  const handleChangeStatut = async (id: number, statut: StatutFacture) => {
    try {
      await factureService.updateStatut(id, statut);
      showToast("Statut mis à jour.", "success");
      await fetchAll();
      setSelectedFacture((prev) => prev?.id === id ? { ...prev, statut } : prev);
    } catch (err: any) {
      showToast(err.response?.data?.detail || "Erreur lors du changement de statut.", "error");
    }
  };

  const handleDownloadPdf = async (id: number) => {
    try {
      const blob = await factureService.genererPdf(id);
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

  // ── Filtering & grouping ──────────────────────────────────────────────────
  const filtered = useMemo(() =>
    filterStatut === "TOUS"
      ? factures
      : factures.filter((f) => f.statut === filterStatut),
    [factures, filterStatut]
  );

  const groupedByMonth = useMemo(() => groupByMonthAndDay(filtered), [filtered]);

  // Flat list for pagination
  const flatPaginated = useMemo(() => {
    return filtered
      .slice()
      .sort((a, b) => new Date(b.date_creation).getTime() - new Date(a.date_creation).getTime())
      .slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  }, [filtered, page]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  const stats = useMemo(() => ({
    total:     factures.length,
    brouillon: factures.filter((f) => f.statut === "BROUILLON").length,
    validee:   factures.filter((f) => f.statut === "VALIDEE").length,
    payee:     factures.filter((f) => f.statut === "PAYEE").length,
    annulee:   factures.filter((f) => f.statut === "ANNULEE").length,
  }), [factures]);

  // ── Show form ─────────────────────────────────────────────────────────────
  if (showForm) {
    return (
      <DocumentForm
        titre="Nouvelle facture"
        numeroApercu="FAC-2025-•••••"
        showEcheance={true}
        labelEcheance="Date d'échéance"
        submitLabel="Créer la facture"
        onCancel={() => {
          setShowForm(false);
          setSearchParams({});
        }}
        onSubmit={handleCreate}
      />
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl text-sm font-medium transition-all ${
          toast.type === "success" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
        }`}>
          {toast.type === "success" ? "✓" : "✕"} {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Factures</h1>
          <p className="text-gray-500 mt-1">Créez et gérez vos factures clients</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
          <Plus className="w-4 h-4 mr-2" /> Nouvelle facture
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total",      count: stats.total,     color: "text-slate-900" },
          { label: "Validées",   count: stats.validee,   color: "text-blue-600" },
          { label: "Payées",     count: stats.payee,     color: "text-emerald-600" },
          { label: "Annulées",   count: stats.annulee,   color: "text-red-500" },
        ].map((s) => (
          <Card key={s.label} className="border border-slate-200 shadow-sm">
            <CardContent className="p-4">
              <p className={`text-2xl font-black ${s.color}`}>{s.count}</p>
              <p className="text-xs font-medium text-slate-400 mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {(["TOUS", "BROUILLON", "VALIDEE", "PAYEE", "ANNULEE"] as const).map((s) => (
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

      {/* Content */}
      {loading ? (
        <Card>
          <CardContent className="py-16 text-center text-slate-400">Chargement...</CardContent>
        </Card>
      ) : filtered.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucune facture</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">
              Créez votre première facture ou convertissez un devis accepté.
            </p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Créer une facture
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Grouped view — one block per month */}
          {Object.entries(groupedByMonth).map(([month, dayGroups]) => (
            <div key={month} className="space-y-3">
              {/* Month header */}
              <div className="flex items-center gap-3">
                <CalendarDays className="w-4 h-4 text-slate-400" />
                <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest">{month}</h2>
                <div className="flex-1 h-px bg-slate-100" />
              </div>

              {Object.entries(dayGroups).map(([day, dayFactures]) => (
                <div key={day} className="space-y-1">
                  {/* Day label */}
                  <p className="text-xs font-semibold text-slate-400 px-1 ml-1">{day}</p>

                  <Card className="border border-slate-200 shadow-sm">
                    <CardContent className="p-0">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-50 border-b border-slate-100">
                          <tr>
                            {["Numéro", "Client", "Statut", "Total HT", "TVA", "Total TTC", "Échéance", "Actions"].map((h) => (
                              <th
                                key={h}
                                className={`px-5 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider ${
                                  ["Total HT", "TVA", "Total TTC"].includes(h) ? "text-right" :
                                  h === "Actions" ? "text-center" : "text-left"
                                }`}
                              >
                                {h}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                          {dayFactures.map((f) => {
                            const client = clientMap[f.client_id] ?? null;
                            return (
                              <tr key={f.id} className="hover:bg-slate-50/60 transition">
                                {/* Numéro */}
                                <td className="px-5 py-3.5 font-mono font-semibold text-blue-600 text-xs">
                                  {f.numero ?? `#${f.id}`}
                                </td>

                                {/* Client + email */}
                                <td className="px-5 py-3.5">
                                  {client ? (
                                    <div>
                                      <p className="font-semibold text-slate-800 text-xs">
                                        {`${client.prenom ?? ""} ${client.nom ?? ""}`.trim() || `Client #${client.id}`}
                                      </p>
                                      <p className="text-blue-500 text-xs">{client.email ?? "—"}</p>
                                    </div>
                                  ) : (
                                    <span className="text-slate-300 italic text-xs">Client #{f.client_id}</span>
                                  )}
                                </td>

                                {/* Statut */}
                                <td className="px-5 py-3.5">
                                  <StatusBadge statut={f.statut} />
                                </td>

                                {/* Montants */}
                                <td className="px-5 py-3.5 text-right text-slate-700 font-medium text-xs tabular-nums">
                                  {formatCurrency(f.total_ht)}
                                </td>
                                <td className="px-5 py-3.5 text-right text-slate-500 text-xs tabular-nums">
                                  {formatCurrency(f.tva)}
                                </td>
                                <td className="px-5 py-3.5 text-right font-bold text-slate-900 text-xs tabular-nums">
                                  {formatCurrency(f.total_ttc)}
                                </td>

                                {/* Échéance */}
                                <td className="px-5 py-3.5 text-xs">
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

                                {/* Actions */}
                                <td className="px-5 py-3.5">
                                  <div className="flex items-center justify-center gap-1.5">
                                    <button
                                      onClick={() => setSelectedFacture(f)}
                                      className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:border-slate-900 hover:text-slate-900 transition"
                                    >
                                      <Eye className="w-3 h-3" /> Voir
                                    </button>
                                    <button
                                      onClick={() => handleDownloadPdf(f.id)}
                                      className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition"
                                    >
                                      <Download className="w-3 h-3" /> PDF
                                    </button>
                                    {f.statut === "BROUILLON" && (
                                      <button
                                        onClick={() => handleChangeStatut(f.id, "VALIDEE")}
                                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:border-slate-900 hover:text-slate-900 transition"
                                      >
                                        <Send className="w-3 h-3" /> Valider
                                      </button>
                                    )}
                                    {f.statut === "VALIDEE" && (
                                      <>
                                        <button
                                          onClick={() => handleChangeStatut(f.id, "PAYEE")}
                                          className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-emerald-200 text-emerald-700 rounded-lg hover:bg-emerald-50 transition"
                                        >
                                          <CheckCircle className="w-3 h-3" /> Payée
                                        </button>
                                        <button
                                          onClick={() => handleChangeStatut(f.id, "ANNULEE")}
                                          className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition"
                                        >
                                          <XCircle className="w-3 h-3" /> Annuler
                                        </button>
                                      </>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-2">
              <span className="text-xs text-slate-400">{filtered.length} facture(s)</span>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline" size="sm" className="h-8 w-8 p-0"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <span className="text-xs text-slate-600 font-medium">Page {page} / {totalPages}</span>
                <Button
                  variant="outline" size="sm" className="h-8 w-8 p-0"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Detail Modal */}
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
