import { useEffect, useState } from "react";
import { ShoppingCart, Plus, CheckCircle, ArrowRight, ChevronLeft, ChevronRight, Download } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { DocumentForm, type DocumentFormData } from "../components/ventes/DocumentForm";
import { bonCommandeService, type BonCommande } from "../../services/ventesService";

const STATUT: Record<string, { label: string; cls: string }> = {
  BROUILLON: { label: "Brouillon", cls: "bg-amber-100 text-amber-700 border-amber-200" },
  CONFIRME:  { label: "Confirmé",  cls: "bg-blue-100 text-blue-700 border-blue-200" },
  EN_COURS:  { label: "En cours",  cls: "bg-yellow-100 text-yellow-700 border-yellow-200" },
  LIVRE:     { label: "Livré",     cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  FACTURE:   { label: "Facturé",   cls: "bg-purple-100 text-purple-700 border-purple-200" },
  ANNULE:    { label: "Annulé",    cls: "bg-red-100 text-red-700 border-red-200" },
};

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUT[statut] ?? { label: statut, cls: "bg-gray-100 text-gray-600 border-gray-200" };
  return <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>{s.label}</span>;
}

export function BonCommandePage() {
  const [bcs, setBcs]         = useState<BonCommande[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [page, setPage]       = useState(1);
  const [total, setTotal]     = useState(0);
  const PAGE_SIZE = 10;

  const fetchBCs = async () => {
    try {
      setLoading(true);
      const data = await bonCommandeService.getAll(page, PAGE_SIZE);
      setBcs(data.items || []); setTotal(data.total || 0);
    } catch { /* silent */ } finally { setLoading(false); }
  };

  useEffect(() => { fetchBCs(); }, [page]);

  const handleCreate = async (data: DocumentFormData) => {
    await bonCommandeService.createManuel({
      client_id: data.client_id,
      notes: data.notes,
      date_livraison_souhaitee: data.date_echeance || null,
      lignes: data.lignes.map(l => ({
        product_id: l.product_id,
        description: l.designation,
        quantite: l.quantite,
        prix_unitaire: l.prix_unitaire,
        taux_tva: l.taux_tva,
        remise: l.remise,
        montant_ht: l.montant_ht,
      })),
    });
    setShowForm(false); fetchBCs();
  };

  const handleConfirmer = async (id: number) => {
    try { await bonCommandeService.changerStatut(id, "CONFIRME"); fetchBCs(); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleConvertirBL = async (id: number) => {
    if (!confirm("Convertir en Bon de livraison ?")) return;
    try { await bonCommandeService.convertirEnBL(id); fetchBCs(); alert("BL créé !"); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleConvertirFacture = async (id: number) => {
    if (!confirm("Facturer directement ce BC ?")) return;
    try { await bonCommandeService.convertirEnFacture(id); fetchBCs(); alert("Facture créée !"); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleDownloadPdf = async (id: number) => {
    try {
      const blob = await bonCommandeService.generatePdf(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bon_commande_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('Erreur lors du téléchargement du PDF');
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  if (showForm) {
    return (
      <DocumentForm
        titre="Nouveau bon de commande"
        numeroApercu="BC-2025-•••••"
        showEcheance={true}
        labelEcheance="Date de livraison souhaitée"
        submitLabel="Créer le bon de commande"
        onCancel={() => setShowForm(false)}
        onSubmit={handleCreate}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bons de commande</h1>
          <p className="text-gray-500 mt-1">Gérez vos commandes clients</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
          <Plus className="w-4 h-4 mr-2" /> Nouveau BC
        </Button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total",     count: total,                                              color: "text-slate-900" },
          { label: "Confirmés", count: bcs.filter(b => b.statut === "CONFIRME").length,   color: "text-blue-600" },
          { label: "En cours",  count: bcs.filter(b => b.statut === "EN_COURS").length,   color: "text-yellow-600" },
          { label: "Livrés",    count: bcs.filter(b => b.statut === "LIVRE").length,      color: "text-emerald-600" },
        ].map(s => (
          <Card key={s.label} className="border border-slate-200 shadow-sm">
            <CardContent className="p-4">
              <p className={`text-2xl font-black ${s.color}`}>{s.count}</p>
              <p className="text-xs font-medium text-slate-400 mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {loading ? (
        <Card><CardContent className="py-16 text-center text-slate-400">Chargement...</CardContent></Card>
      ) : bcs.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <ShoppingCart className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucun bon de commande</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">Créez un BC manuellement ou convertissez un devis accepté.</p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Nouveau BC
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {["Numéro", "Client", "Statut", "Montant TTC", "Date", "Actions"].map(h => (
                    <th key={h} className={`px-6 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider ${h === "Montant TTC" ? "text-right" : h === "Actions" ? "text-center" : "text-left"}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {bcs.map(bc => (
                  <tr key={bc.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-6 py-4 font-mono font-semibold text-blue-600 text-xs">{bc.numero}</td>
                    <td className="px-6 py-4 text-slate-700 font-medium">{bc.client_id}</td>
                    <td className="px-6 py-4"><StatusBadge statut={bc.statut} /></td>
                    <td className="px-6 py-4 text-right font-semibold text-slate-900">
                      {bc.montant_ttc?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-xs">{new Date(bc.date_creation).toLocaleDateString("fr-FR")}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-1.5">
                        <button onClick={() => handleDownloadPdf(bc.id)}
                          className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition">
                          <Download className="w-3 h-3" /> PDF
                        </button>
                        {bc.statut === "BROUILLON" && (
                          <button onClick={() => handleConfirmer(bc.id)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition">
                            <CheckCircle className="w-3 h-3" /> Confirmer
                          </button>
                        )}
                        {bc.statut === "CONFIRME" && (
                          <>
                            <button onClick={() => handleConvertirBL(bc.id)}
                              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-emerald-200 text-emerald-700 rounded-lg hover:bg-emerald-50 transition">
                              <ArrowRight className="w-3 h-3" /> → BL
                            </button>
                            <button onClick={() => handleConvertirFacture(bc.id)}
                              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-purple-200 text-purple-700 rounded-lg hover:bg-purple-50 transition">
                              <ArrowRight className="w-3 h-3" /> → Facture
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">{total} bons de commande</span>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}><ChevronLeft className="w-4 h-4" /></Button>
                  <span className="text-xs text-slate-600 font-medium">Page {page} / {totalPages}</span>
                  <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}><ChevronRight className="w-4 h-4" /></Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}