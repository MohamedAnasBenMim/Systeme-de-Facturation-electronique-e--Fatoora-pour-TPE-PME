import { useEffect, useState } from "react";
import { Plus, Building2, Phone, Mail, ChevronLeft, ChevronRight, Pencil } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { fournisseurService, type Fournisseur } from "../../services/achatsService";
import { FournisseurForm } from "../components/achats/FournisseurForm";

function StatusBadge({ actif }: { actif: boolean }) {
  return actif ? (
    <span className="inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border bg-emerald-100 text-emerald-700 border-emerald-200">
      Actif
    </span>
  ) : (
    <span className="inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border bg-gray-100 text-gray-500 border-gray-200">
      Inactif
    </span>
  );
}

export function FournisseursPage() {
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading]           = useState(true);
  const [showForm, setShowForm]         = useState(false);
  const [editing, setEditing]           = useState<Fournisseur | null>(null);
  const [page, setPage]                 = useState(1);
  const PAGE_SIZE = 10;

  const fetchData = async () => {
    try {
      setLoading(true);
      // actifs_seulement=false pour tout afficher
      setFournisseurs(await fournisseurService.getAll(false));
    } catch (e) {
      console.error("Erreur chargement fournisseurs", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (data: Partial<Fournisseur>) => {
    try {
      if (editing) await fournisseurService.update(editing.id, data);
      else         await fournisseurService.create(data);
      setShowForm(false);
      setEditing(null);
      fetchData();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur lors de l'enregistrement");
    }
  };

  const paginated  = fournisseurs.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.ceil(fournisseurs.length / PAGE_SIZE);

  if (showForm || editing) {
    return (
      <FournisseurForm
        initial={editing ?? undefined}
        onCancel={() => { setShowForm(false); setEditing(null); }}
        onSubmit={handleSubmit}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fournisseurs</h1>
          <p className="text-gray-500 mt-1">Gérez vos fournisseurs et leurs conditions</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
          <Plus className="w-4 h-4 mr-2" /> Nouveau fournisseur
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total",   count: fournisseurs.length,                           color: "text-slate-900" },
          { label: "Actifs",  count: fournisseurs.filter(f => f.actif).length,      color: "text-emerald-600" },
          { label: "Inactifs",count: fournisseurs.filter(f => !f.actif).length,     color: "text-gray-500" },
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
      ) : fournisseurs.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <Building2 className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucun fournisseur</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">
              Ajoutez votre premier fournisseur pour commencer à gérer vos achats.
            </p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Ajouter un fournisseur
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {["Nom", "Matricule Fiscale", "Contact", "Statut", "Actions"].map(h => (
                    <th key={h} className="px-6 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider text-left">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {paginated.map(f => (
                  <tr key={f.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-6 py-4">
                      {/*  f.nom — vrai champ du modèle */}
                      <div className="font-semibold text-slate-900">{f.nom}</div>
                      <div className="text-xs text-slate-400">{f.ville}</div>
                    </td>
                    {/*  f.matricule_fiscal — vrai champ du modèle */}
                    <td className="px-6 py-4 font-mono text-xs text-slate-600">{f.matricule_fiscal}</td>
                    <td className="px-6 py-4">
                      {f.email && (
                        <div className="flex items-center gap-1 text-xs text-slate-500">
                          <Mail className="w-3 h-3" /> {f.email}
                        </div>
                      )}
                      {f.telephone && (
                        <div className="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                          <Phone className="w-3 h-3" /> {f.telephone}
                        </div>
                      )}
                    </td>
                    {/*  f.delai_paiement_jours — vrai champ du modèle */}
                    {/*  f.actif — vrai champ du modèle */}
                    <td className="px-6 py-4"><StatusBadge actif={f.actif} /></td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setEditing(f)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:border-slate-900 hover:text-slate-900 transition"
                      >
                        <Pencil className="w-3 h-3" /> Modifier
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">{fournisseurs.length} fournisseurs</span>
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