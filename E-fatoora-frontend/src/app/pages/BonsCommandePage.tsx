import { useEffect, useState } from "react";
import { Plus, ShoppingCart, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  bonCommandeService,
  receptionService,
  fournisseurService,
  type BonCommande,
  type Fournisseur,
} from "../../services/achatsService";
import { BonCommandeForm } from "../components/achats/BonCommandeForm";

// ✅ Statuts en MAJUSCULES — alignés sur l'enum Python StatutBonCommande
const STATUT: Record<string, { label: string; cls: string }> = {
  BROUILLON:     { label: "Brouillon",        cls: "bg-amber-100 text-amber-700 border-amber-200" },
  CONFIRMEE:     { label: "Confirmé",         cls: "bg-blue-100 text-blue-700 border-blue-200" },
  LIVREE:        { label: "Livré",            cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  DIFFERENCIEE:  { label: "Écart détecté",    cls: "bg-orange-100 text-orange-700 border-orange-200" },
};

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUT[statut] ?? { label: statut, cls: "bg-gray-100 text-gray-500 border-gray-200" };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>
      {s.label}
    </span>
  );
}

export function BonsCommandePage() {
  const [bons, setBons]         = useState<BonCommande[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading]   = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [page, setPage]         = useState(1);
  const PAGE_SIZE = 10;

  const fetchData = async () => {
    try {
      setLoading(true);
      const [bonsData, foursData] = await Promise.all([
        bonCommandeService.getAll(),
        fournisseurService.getAll(false),
      ]);
      setBons(bonsData);
      setFournisseurs(foursData);
    } catch (e) {
      console.error("Erreur chargement bons de commande", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  // Résoudre le nom du fournisseur localement
  const getNomFournisseur = (id: number) =>
    fournisseurs.find(f => f.id === id)?.nom ?? `Fournisseur #${id}`;

  const handleConfirmer = async (id: number) => {
    if (!confirm("Confirmer ce bon de commande ? Il ne pourra plus être modifié.")) return;
    try {
      await bonCommandeService.confirmer(id);
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur lors de la confirmation");
    }
  };

  const handleCreate = async (data: Partial<BonCommande>) => {
    try {
      await bonCommandeService.create(data);
      setShowForm(false);
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur lors de la création");
    }
  };

  const paginated  = bons.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.ceil(bons.length / PAGE_SIZE);

  if (showForm) {
    return (
      <BonCommandeForm
        fournisseurs={fournisseurs}
        onCancel={() => setShowForm(false)}
        onSubmit={handleCreate}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bons de Commande</h1>
          <p className="text-gray-500 mt-1">Gérez vos commandes fournisseurs</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
          <Plus className="w-4 h-4 mr-2" /> Nouveau bon de commande
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total",      count: bons.length,                                         color: "text-slate-900" },
          { label: "Brouillons", count: bons.filter(b => b.statut === "BROUILLON").length,   color: "text-amber-600" },
          { label: "Confirmés",  count: bons.filter(b => b.statut === "CONFIRMEE").length,   color: "text-blue-600" },
          { label: "Livrés",     count: bons.filter(b => b.statut === "LIVREE").length,      color: "text-emerald-600" },
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
      ) : bons.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <ShoppingCart className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucun bon de commande</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">
              Créez votre premier bon de commande pour commander auprès de vos fournisseurs.
            </p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Créer un bon de commande
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {["Numéro BC", "Fournisseur", "Statut", "Total TTC", "Date création", "Livraison prévue", "Actions"].map(h => (
                    <th key={h} className={`px-6 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider ${h === "Total TTC" ? "text-right" : "text-left"}`}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {paginated.map(b => (
                  <tr key={b.id} className="hover:bg-slate-50/60 transition">
                    {/* ✅ b.numero_bc — vrai champ du modèle */}
                    <td className="px-6 py-4 font-mono font-semibold text-blue-600 text-xs">{b.numero_bc}</td>
                    {/* ✅ getNomFournisseur résout le nom depuis la liste locale */}
                    <td className="px-6 py-4 text-slate-700 font-medium">{getNomFournisseur(b.fournisseur_id)}</td>
                    {/* ✅ b.statut en MAJUSCULES */}
                    <td className="px-6 py-4"><StatusBadge statut={b.statut} /></td>
                    <td className="px-6 py-4 text-right font-semibold text-slate-900">
                      {b.total_ttc?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                    </td>
                    {/* ✅ b.date_creation — vrai champ du modèle */}
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {new Date(b.date_creation).toLocaleDateString("fr-FR")}
                    </td>
                    {/* ✅ b.date_livraison_attendue — vrai champ du modèle */}
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {b.date_livraison_attendue
                        ? new Date(b.date_livraison_attendue).toLocaleDateString("fr-FR")
                        : "—"}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5">
                        {b.statut === "BROUILLON" && (
                          <button
                            onClick={() => handleConfirmer(b.id)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold bg-slate-900 text-white rounded-lg hover:bg-slate-700 transition"
                          >
                            <CheckCircle className="w-3 h-3" /> Confirmer
                          </button>
                        )}
                        {b.statut === "CONFIRMEE" && (
                          <ReceptionModal bc={b} onDone={fetchData} />
                        )}
                        {b.statut === "LIVREE" && (
                          <span className="text-xs text-emerald-600 font-semibold">✓ Livré</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">{bons.length} bons de commande</span>
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

// ─── Modal Réception rapide ────────────────────────────────────────────────────
function ReceptionModal({ bc, onDone }: { bc: BonCommande; onDone: () => void }) {
  const [open, setOpen]       = useState(false);
  const [date, setDate]       = useState(new Date().toISOString().split("T")[0]);
  const [numeroBl, setNumeroBl] = useState("");
  const [quantities, setQty]  = useState<Record<number, { conforme: number; non_conforme: number }>>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await receptionService.create({
        bon_commande_id: bc.id,
        fournisseur_id: bc.fournisseur_id,
        entreprise_id: bc.entreprise_id,
        date_reception: date,
        numero_bl: numeroBl || undefined,
        // ✅ lignes alignées sur LigneReception du vrai modèle
        lignes: bc.lignes
          .filter(l => (quantities[l.id!]?.conforme ?? 0) + (quantities[l.id!]?.non_conforme ?? 0) > 0)
          .map(l => ({
            ligne_bc_id: l.id!,
            quantite_receptionnee: (quantities[l.id!]?.conforme ?? 0) + (quantities[l.id!]?.non_conforme ?? 0),
            quantite_conforme: quantities[l.id!]?.conforme ?? 0,
            quantite_non_conforme: quantities[l.id!]?.non_conforme ?? 0,
            conformite_acceptee: (quantities[l.id!]?.non_conforme ?? 0) === 0,
          })),
      });
      setOpen(false);
      onDone();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-emerald-200 text-emerald-700 rounded-lg hover:bg-emerald-50 transition"
      >
        <CheckCircle className="w-3 h-3" /> Réceptionner
      </button>

      {open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-100 sticky top-0 bg-white">
              <h3 className="font-bold text-gray-900">Enregistrer une réception</h3>
              {/* ✅ b.numero_bc */}
              <p className="text-xs text-gray-400 font-mono mt-1">{bc.numero_bc}</p>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Date de réception *</label>
                  <input
                    type="date"
                    value={date}
                    max={new Date().toISOString().split("T")[0]}
                    onChange={e => setDate(e.target.value)}
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">N° bon de livraison fournisseur</label>
                  <input
                    value={numeroBl}
                    onChange={e => setNumeroBl(e.target.value)}
                    placeholder="BL-2024-001"
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-600">
                  Quantités reçues par ligne
                </label>
                {bc.lignes.map(ligne => {
                  const restant = ligne.quantite_commandee - (ligne.quantite_receptionnee ?? 0);
                  return (
                    <div key={ligne.id} className="p-3 bg-slate-50 rounded-lg space-y-2">
                      <div className="flex justify-between">
                        {/* ✅ ligne.designation — vrai champ du modèle */}
                        <p className="text-sm font-medium text-slate-800">{ligne.designation}</p>
                        <p className="text-xs text-slate-400">Restant : {restant}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="text-xs text-emerald-600 font-medium">Conformes</label>
                          <input
                            type="number" min={0} max={restant}
                            value={quantities[ligne.id!]?.conforme ?? 0}
                            onChange={e => setQty(q => ({
                              ...q,
                              [ligne.id!]: { ...q[ligne.id!], conforme: parseInt(e.target.value) || 0 }
                            }))}
                            className="w-full border border-slate-200 rounded px-2 py-1 text-sm text-right mt-0.5"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-red-500 font-medium">Non conformes</label>
                          <input
                            type="number" min={0} max={restant}
                            value={quantities[ligne.id!]?.non_conforme ?? 0}
                            onChange={e => setQty(q => ({
                              ...q,
                              [ligne.id!]: { ...q[ligne.id!], non_conforme: parseInt(e.target.value) || 0 }
                            }))}
                            className="w-full border border-slate-200 rounded px-2 py-1 text-sm text-right mt-0.5"
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="px-6 pb-6 flex gap-3 sticky bottom-0 bg-white border-t border-slate-100 pt-4">
              <button onClick={() => setOpen(false)} className="flex-1 py-2.5 text-sm text-gray-500 border border-gray-200 rounded-xl hover:bg-gray-50 transition">
                Annuler
              </button>
              <button onClick={handleSubmit} disabled={loading} className="flex-1 py-2.5 text-sm font-semibold bg-slate-900 text-white rounded-xl hover:bg-slate-700 transition disabled:opacity-50">
                {loading ? "Enregistrement..." : "Enregistrer la réception"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}