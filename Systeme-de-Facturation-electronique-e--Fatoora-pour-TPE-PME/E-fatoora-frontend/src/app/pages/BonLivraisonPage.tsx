import { useEffect, useState } from "react";
import { Truck, Plus, CheckCircle, XCircle, ArrowRight, Package, ChevronLeft, ChevronRight, Download } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { DocumentForm, type DocumentFormData } from "../components/ventes/DocumentForm";
import { bonLivraisonService, type BonLivraison } from "../../services/ventesService";
import api from "../../services/api";

const STATUT: Record<string, { label: string; cls: string }> = {
  EN_ATTENTE: { label: "En attente", cls: "bg-amber-100 text-amber-700 border-amber-200" },
  EN_COURS:   { label: "En cours",   cls: "bg-blue-100 text-blue-700 border-blue-200" },
  PARTIEL:    { label: "Partiel",    cls: "bg-orange-100 text-orange-700 border-orange-200" },
  LIVRE:      { label: "Livré",      cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  ANNULE:     { label: "Annulé",     cls: "bg-red-100 text-red-700 border-red-200" },
  FACTURE:    { label: "Facturé",    cls: "bg-purple-100 text-purple-700 border-purple-200" },
};

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUT[statut] ?? { label: statut, cls: "bg-gray-100 text-gray-600 border-gray-200" };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>
      {s.label}
    </span>
  );
}

export function BonLivraisonPage() {
  const [bls, setBls]           = useState<BonLivraison[]>([]);
  const [loading, setLoading]   = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [page, setPage]         = useState(1);
  const [total, setTotal]       = useState(0);
  const [selected, setSelected] = useState<number[]>([]);
  const PAGE_SIZE = 10;

  const fetchBLs = async () => {
    try {
      setLoading(true);
      const data = await bonLivraisonService.getAll(page, PAGE_SIZE);
      setBls(data.items || []);
      setTotal(data.total || 0);
    } catch { /* silent */ }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchBLs(); }, [page]);

  // Création directe d'un BL manuel
  const handleCreate = async (data: DocumentFormData) => {
    await api.post("/bon-livraison/", {
      client_id: data.client_id,
      notes: data.notes,
      date_livraison: data.date_echeance || null,
      lignes: data.lignes.map(l => ({
        product_id: l.product_id,
        description: l.designation,
        quantite: l.quantite,
        quantite_livree: l.quantite,     // par défaut : tout livré
        prix_unitaire: l.prix_unitaire,
        taux_tva: l.taux_tva,
        remise: l.remise,
        montant_ht: l.montant_ht,
      })),
    });
    setShowForm(false);
    fetchBLs();
  };

  const handleConfirmer = async (id: number) => {
    if (!confirm("Confirmer la livraison complète ?")) return;
    try { await bonLivraisonService.confirmer(id); fetchBLs(); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleAnnuler = async (id: number) => {
    if (!confirm("Annuler ce bon de livraison ?")) return;
    try { await bonLivraisonService.annuler(id); fetchBLs(); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handlePartiel = async (id: number) => {
    if (!confirm("Créer un BL reliquat pour les quantités non livrées ?")) return;
    try { await bonLivraisonService.creerPartiel(id); fetchBLs(); alert("BL reliquat créé !"); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleFacture = async (id: number) => {
    if (!confirm("Convertir ce BL en facture ?")) return;
    try { await bonLivraisonService.convertirEnFacture(id); fetchBLs(); alert("Facture créée !"); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleFactureGroupee = async () => {
    if (selected.length < 2) return alert("Sélectionnez au moins 2 BL livrés.");
    if (!confirm(`Créer une facture groupée pour ${selected.length} BL ?`)) return;
    try {
      await bonLivraisonService.convertirGroupeEnFacture(selected);
      setSelected([]); fetchBLs(); alert("Facture groupée créée !");
    } catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleDownloadPdf = async (id: number) => {
    try {
      const blob = await bonLivraisonService.generatePdf(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bon_livraison_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('Erreur lors du téléchargement du PDF');
    }
  };

  const toggleSelect = (id: number) =>
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const livresTotaux = bls.filter(b => b.statut === "LIVRE" && !b.facture_id_externe);

  // ── Formulaire plein écran ─────────────────────────────────
  if (showForm) {
    return (
      <DocumentForm
        titre="Nouveau bon de livraison"
        numeroApercu="BL-2025-•••••"
        showEcheance={true}
        labelEcheance="Date de livraison prévue"
        submitLabel="Créer le bon de livraison"
        onCancel={() => setShowForm(false)}
        onSubmit={handleCreate}
      />
    );
  }

  // ── Liste ──────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bons de livraison</h1>
          <p className="text-gray-500 mt-1">Gérez vos livraisons et générez vos factures</p>
        </div>
        <div className="flex items-center gap-3">
          {selected.length > 0 && (
            <Button onClick={handleFactureGroupee} className="bg-purple-600 hover:bg-purple-700">
              <Package className="w-4 h-4 mr-2" />
              Facture groupée ({selected.length} BL)
            </Button>
          )}
          <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
            <Plus className="w-4 h-4 mr-2" /> Nouveau BL
          </Button>
        </div>
      </div>

      {/* Bandeau sélection groupée */}
      {livresTotaux.length > 0 && selected.length === 0 && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3 flex items-center justify-between">
          <p className="text-sm text-blue-700">
            <span className="font-semibold">{livresTotaux.length} BL livré(s)</span> prêts à être facturés
          </p>
          <p className="text-xs text-blue-400">Cochez les BL pour créer une facture groupée</p>
        </div>
      )}
      {selected.length > 0 && (
        <div className="bg-purple-50 border border-purple-100 rounded-xl px-4 py-3 flex items-center justify-between">
          <p className="text-sm text-purple-700 font-medium">{selected.length} BL sélectionné(s)</p>
          <button onClick={() => setSelected([])} className="text-xs text-purple-500 underline hover:text-purple-700">
            Tout désélectionner
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total",      count: total,                                                   color: "text-slate-900" },
          { label: "En attente", count: bls.filter(b => b.statut === "EN_ATTENTE").length,       color: "text-amber-600" },
          { label: "Livrés",     count: bls.filter(b => b.statut === "LIVRE").length,            color: "text-emerald-600" },
          { label: "Facturés",   count: bls.filter(b => b.statut === "FACTURE").length,          color: "text-purple-600" },
        ].map(s => (
          <Card key={s.label} className="border border-slate-200 shadow-sm">
            <CardContent className="p-4">
              <p className={`text-2xl font-black ${s.color}`}>{s.count}</p>
              <p className="text-xs font-medium text-slate-400 mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <Card><CardContent className="py-16 text-center text-slate-400">Chargement...</CardContent></Card>
      ) : bls.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <Truck className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucun bon de livraison</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">
              Créez un BL directement ou convertissez un devis / bon de commande.
            </p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Nouveau BL
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-4 py-3.5 w-10 text-center text-xs text-slate-400">☐</th>
                  {["Numéro", "Source", "Client", "Statut", "Montant TTC", "Date", "Actions"].map(h => (
                    <th key={h} className={`px-4 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider ${
                      h === "Montant TTC" ? "text-right" : h === "Actions" ? "text-center" : "text-left"
                    }`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {bls.map(bl => (
                  <tr key={bl.id} className={`hover:bg-slate-50/60 transition ${selected.includes(bl.id) ? "bg-purple-50/60" : ""}`}>
                    <td className="px-4 py-4 text-center">
                      {bl.statut === "LIVRE" && !bl.facture_id_externe && (
                        <input type="checkbox" checked={selected.includes(bl.id)}
                          onChange={() => toggleSelect(bl.id)}
                          className="cursor-pointer accent-purple-600 w-4 h-4" />
                      )}
                    </td>
                    <td className="px-4 py-4 font-mono font-semibold text-blue-600 text-xs">{bl.numero}</td>
                    <td className="px-4 py-4 text-slate-400 text-xs">{bl.source?.replace("_", " ") || "MANUEL"}</td>
                    <td className="px-4 py-4 text-slate-700 font-medium">{bl.client_id}</td>
                    <td className="px-4 py-4"><StatusBadge statut={bl.statut} /></td>
                    <td className="px-4 py-4 text-right font-semibold text-slate-900">
                      {bl.montant_ttc?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                    </td>
                    <td className="px-4 py-4 text-slate-400 text-xs">
                      {new Date(bl.date_creation).toLocaleDateString("fr-FR")}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center justify-center gap-1.5 flex-wrap">
                        <button onClick={() => handleDownloadPdf(bl.id)}
                          className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition">
                          <Download className="w-3 h-3" /> PDF
                        </button>
                        {(bl.statut === "EN_ATTENTE" || bl.statut === "EN_COURS") && (
                          <button onClick={() => handleConfirmer(bl.id)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-emerald-200 text-emerald-700 rounded-lg hover:bg-emerald-50 transition">
                            <CheckCircle className="w-3 h-3" /> Confirmer
                          </button>
                        )}
                        {bl.statut === "PARTIEL" && (
                          <button onClick={() => handlePartiel(bl.id)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-orange-200 text-orange-700 rounded-lg hover:bg-orange-50 transition">
                            <Package className="w-3 h-3" /> Reliquat
                          </button>
                        )}
                        {bl.statut === "LIVRE" && !bl.facture_id_externe && (
                          <button onClick={() => handleFacture(bl.id)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold bg-slate-900 text-white rounded-lg hover:bg-slate-700 transition">
                            <ArrowRight className="w-3 h-3" /> Facture
                          </button>
                        )}
                        {(bl.statut === "EN_ATTENTE" || bl.statut === "EN_COURS") && (
                          <button onClick={() => handleAnnuler(bl.id)}
                            className="w-7 h-7 flex items-center justify-center text-red-400 hover:bg-red-50 rounded-lg transition">
                            <XCircle className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">{total} bons de livraison</span>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="h-8 w-8 p-0"
                    onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-xs text-slate-600 font-medium">Page {page} / {totalPages}</span>
                  <Button variant="outline" size="sm" className="h-8 w-8 p-0"
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}