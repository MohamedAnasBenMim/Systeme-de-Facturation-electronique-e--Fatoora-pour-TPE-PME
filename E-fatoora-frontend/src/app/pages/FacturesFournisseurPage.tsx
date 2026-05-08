import { useEffect, useState } from "react";
import { Plus, FileText, AlertTriangle, ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  factureAchatService,
  fournisseurService,
  type FactureFournisseur,
  type Fournisseur,
} from "../../services/achatsService";
import { FactureFournisseurForm } from "../components/achats/FactureFournisseurForm";

//  Statuts alignés sur StatutFactureFournisseur de Python
const STATUT: Record<string, { label: string; cls: string }> = {
  BROUILLON:          { label: "Brouillon",          cls: "bg-slate-100 text-slate-600 border-slate-200" },
  EN_RAPPROCHEMENT:   { label: "En rapprochement",   cls: "bg-blue-100 text-blue-700 border-blue-200" },
  EN_LITIGE:          { label: "En litige",           cls: "bg-red-100 text-red-600 border-red-200" },
  VALIDEE:            { label: "Validée",             cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  PAYEE:              { label: "Payée",               cls: "bg-purple-100 text-purple-700 border-purple-200" },
};

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUT[statut] ?? { label: statut, cls: "bg-gray-100 text-gray-500 border-gray-200" };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>
      {s.label}
    </span>
  );
}

export function FacturesFournisseurPage() {
  const [factures, setFactures]       = useState<FactureFournisseur[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading]         = useState(true);
  const [showForm, setShowForm]       = useState(false);
  const [page, setPage]               = useState(1);
  const PAGE_SIZE = 10;

  const fetchData = async () => {
    try {
      setLoading(true);
      const [facturesData, foursData] = await Promise.all([
        factureAchatService.getAll(),
        fournisseurService.getAll(false),
      ]);
      setFactures(facturesData);
      setFournisseurs(foursData);
    } catch (e) {
      console.error("Erreur chargement factures", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const getNomFournisseur = (id: number) =>
    fournisseurs.find(f => f.id === id)?.nom ?? `Fournisseur #${id}`;

  const handleCreate = async (data: Partial<FactureFournisseur>) => {
    try {
      await factureAchatService.create(data);
      setShowForm(false);
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur lors de la création");
    }
  };

  //  date_echeance — vrai champ du modèle
  const isOverdue = (f: FactureFournisseur) =>
    f.statut !== "PAYEE" && f.date_echeance && new Date(f.date_echeance) < new Date();

  const paginated  = factures.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.ceil(factures.length / PAGE_SIZE);

  if (showForm) {
    return (
      <FactureFournisseurForm
        onCancel={() => setShowForm(false)}
        onSubmit={handleCreate}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Factures Fournisseurs</h1>
          <p className="text-gray-500 mt-1">Saisissez et suivez vos factures d'achat</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
          <Plus className="w-4 h-4 mr-2" /> Saisir une facture
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total",           count: factures.length,                                           color: "text-slate-900" },
          { label: "En rapprochement",count: factures.filter(f => f.statut === "EN_RAPPROCHEMENT").length, color: "text-blue-600" },
          { label: "En litige",       count: factures.filter(f => f.statut === "EN_LITIGE").length,     color: "text-red-500" },
          { label: "Validées",        count: factures.filter(f => f.statut === "VALIDEE").length,       color: "text-emerald-600" },
        ].map(s => (
          <Card key={s.label} className="border border-slate-200 shadow-sm">
            <CardContent className="p-4">
              <p className={`text-2xl font-black ${s.color}`}>{s.count}</p>
              <p className="text-xs font-medium text-slate-400 mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Alerte litiges */}
      {factures.filter(f => f.statut === "EN_LITIGE").length > 0 && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700 font-medium">
            {factures.filter(f => f.statut === "EN_LITIGE").length} facture(s) bloquée(s) en litige — rapprochement 3 voies échoué.
            Rendez-vous dans l'onglet Litiges pour les résoudre.
          </p>
        </div>
      )}

      {loading ? (
        <Card><CardContent className="py-16 text-center text-slate-400">Chargement...</CardContent></Card>
      ) : factures.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucune facture</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">
              Saisissez votre première facture fournisseur pour commencer le suivi.
            </p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Saisir une facture
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {["N° Facture interne", "N° Fournisseur", "Fournisseur", "Statut", "Total HT", "Total TTC net", "Date facture", "Échéance"].map(h => (
                    <th key={h} className={`px-6 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider ${["Total HT","Total TTC net"].includes(h) ? "text-right" : "text-left"}`}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {paginated.map(f => (
                  <tr key={f.id} className={`hover:bg-slate-50/60 transition ${isOverdue(f) ? "bg-orange-50/40" : ""}`}>
                    {/* ✅ f.numero_facture — numéro interne généré */}
                    <td className="px-6 py-4 font-mono font-semibold text-blue-600 text-xs">{f.numero_facture}</td>
                    {/* Pas de champ supplier_invoice_number dans ce modèle → on affiche la ref BC fournisseur */}
                    <td className="px-6 py-4 font-mono text-xs text-slate-500">
                      {f.reference_bon_commande_fournisseur ?? "—"}
                    </td>
                    {/* ✅ getNomFournisseur via fournisseur_id */}
                    <td className="px-6 py-4 text-slate-700 font-medium">{getNomFournisseur(f.fournisseur_id)}</td>
                    {/* ✅ f.statut en MAJUSCULES */}
                    <td className="px-6 py-4"><StatusBadge statut={f.statut} /></td>
                    <td className="px-6 py-4 text-right font-medium text-slate-700">
                      {f.total_ht?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                    </td>
                    {/* ✅ f.total_ttc_net — montant après avoirs */}
                    <td className="px-6 py-4 text-right font-semibold text-slate-900">
                      {f.total_ttc_net?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                    </td>
                    {/* ✅ f.date_facture */}
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {f.date_facture ? new Date(f.date_facture).toLocaleDateString("fr-FR") : "—"}
                    </td>
                    {/* ✅ f.date_echeance */}
                    <td className={`px-6 py-4 text-xs font-medium ${isOverdue(f) ? "text-orange-600" : "text-slate-400"}`}>
                      {f.date_echeance ? new Date(f.date_echeance).toLocaleDateString("fr-FR") : "—"}
                      {isOverdue(f) && <span className="ml-1">⚠️</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">{factures.length} factures</span>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-xs text-slate-600 font-medium">Page {page} / {totalPages}</span>
                  <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
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