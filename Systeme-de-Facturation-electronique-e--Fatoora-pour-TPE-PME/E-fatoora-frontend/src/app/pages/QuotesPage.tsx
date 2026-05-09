import { useEffect, useState } from "react";
import { FileEdit, Plus, Send, CheckCircle, XCircle, ArrowRight, Trash2, ChevronLeft, ChevronRight, Download } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { DocumentForm, type DocumentFormData } from "../components/ventes/DocumentForm";
import { devisService, type Devis } from "../../services/ventesService";
import { getClients } from "../../services/clientService";

const STATUT: Record<string, { label: string; cls: string }> = {
  BROUILLON: { label: "Brouillon", cls: "bg-amber-100 text-amber-700 border-amber-200" },
  ENVOYE:    { label: "Envoyé",    cls: "bg-blue-100 text-blue-700 border-blue-200" },
  ACCEPTE:   { label: "Accepté",   cls: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  REFUSE:    { label: "Refusé",    cls: "bg-red-100 text-red-700 border-red-200" },
  EXPIRE:    { label: "Expiré",    cls: "bg-gray-100 text-gray-600 border-gray-200" },
  CONVERTI:  { label: "Converti",  cls: "bg-purple-100 text-purple-700 border-purple-200" },
};

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUT[statut] ?? { label: statut, cls: "bg-gray-100 text-gray-600 border-gray-200" };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border ${s.cls}`}>
      {s.label}
    </span>
  );
}

function ConversionModal({ devis, onClose, onDone }: { devis: Devis; onClose: () => void; onDone: () => void }) {
  const [loading, setLoading] = useState<string | null>(null);
  const convert = async (type: "bc" | "bl" | "facture") => {
    setLoading(type);
    try {
      if (type === "bc")      await devisService.convertirEnBC(devis.id);
      if (type === "bl")      await devisService.convertirEnBL(devis.id);
      if (type === "facture") await devisService.convertirEnFacture(devis.id);
      onDone();
    } catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
    finally { setLoading(null); }
  };
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="font-bold text-gray-900">Convertir le devis</h3>
          <p className="text-xs text-gray-400 font-mono mt-1">{devis.numero}</p>
        </div>
        <div className="p-4 space-y-2">
          {[
            { type: "bc" as const,      icon: "📋", label: "Bon de commande",  desc: "Flux standard" },
            { type: "bl" as const,      icon: "🚚", label: "Bon de livraison", desc: "Sans BC intermédiaire" },
            { type: "facture" as const, icon: "🧾", label: "Facture",          desc: "Facturation directe" },
          ].map(o => (
            <button key={o.type} onClick={() => convert(o.type)} disabled={!!loading}
              className="w-full text-left px-4 py-3.5 rounded-xl border-2 border-gray-100 hover:border-slate-900 hover:bg-slate-50 transition disabled:opacity-50">
              <div className="flex items-center gap-3">
                <span className="text-xl">{o.icon}</span>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-800">{o.label}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{o.desc}</p>
                </div>
                {loading === o.type && <span className="text-xs text-blue-500 animate-pulse">En cours...</span>}
              </div>
            </button>
          ))}
        </div>
        <div className="px-4 pb-4">
          <button onClick={onClose} className="w-full py-2.5 text-sm text-gray-500 border border-gray-200 rounded-xl hover:bg-gray-50 transition">
            Annuler
          </button>
        </div>
      </div>
    </div>
  );
}

export function QuotesPage() {
  const [devis, setDevis]               = useState<Devis[]>([]);
  const [loading, setLoading]           = useState(true);
  const [showForm, setShowForm]         = useState(false);
  const [converting, setConverting]     = useState<Devis | null>(null);
  const [page, setPage]                 = useState(1);
  // ✅ Map client_id → email
  const [clientMap, setClientMap]       = useState<Record<number, string>>({});
  const PAGE_SIZE = 10;

  // ✅ Charge les clients et construit le map id → email
  const fetchClients = async () => {
    try {
      const data = await getClients();
      const map: Record<number, string> = {};
      (data.clients ?? []).forEach((c: any) => {
        map[c.id] = c.email;
      });
      setClientMap(map);
    } catch {
      // silencieux — la liste s'affiche quand même
    }
  };

  const fetchDevis = async () => {
    try {
      setLoading(true);
      const res: any = await devisService.getAll();
      const list: Devis[] = Array.isArray(res)
        ? res
        : Array.isArray(res?.items)
          ? res.items
          : [];
      list.sort((a, b) => (a.numero || "").localeCompare(b.numero || "", undefined, { numeric: true }));
      setDevis(list);
    } catch {
      /* silent */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
    fetchDevis();
  }, []);

  const handleCreate = async (data: DocumentFormData) => {
    await devisService.create({
      client_id: data.client_id,
      notes: data.notes,
      date_expiration: data.date_echeance || null,
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
    setShowForm(false);
    fetchDevis();
  };

  const handleAction = async (id: number, action: "envoyer" | "accepter" | "refuser") => {
    try { await devisService[action](id); fetchDevis(); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Supprimer ce devis ?")) return;
    try { await devisService.delete(id); fetchDevis(); }
    catch (e: any) { alert(e.response?.data?.detail || "Erreur"); }
  };

  const handleDownloadPdf = async (id: number) => {
    try {
      const blob = await devisService.generatePdf(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `devis_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Erreur lors du téléchargement du PDF");
    }
  };

  // ✅ Calcul du montant TTC depuis les lignes si montant_ttc est null/0
  const getMontantTTC = (d: Devis): number => {
    if (d.montant_ttc != null && d.montant_ttc > 0) return d.montant_ttc;
    if (d.lignes && d.lignes.length > 0) {
      return d.lignes.reduce((acc, l) => {
        const ht  = l.montant_ht ?? l.quantite * l.prix_unitaire;
        const tva = ht * ((l.taux_tva ?? 0) / 100);
        return acc + ht + tva;
      }, 0);
    }
    return 0;
  };

  const paginated  = devis.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.ceil(devis.length / PAGE_SIZE);

  if (showForm) {
    return (
      <DocumentForm
        titre="Nouveau devis"
        numeroApercu="DEV-2025-•••••"
        showEcheance={true}
        labelEcheance="Date d'expiration"
        submitLabel="Créer le devis"
        onCancel={() => setShowForm(false)}
        onSubmit={handleCreate}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Devis</h1>
          <p className="text-gray-500 mt-1">Créez et gérez vos devis clients</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
          <Plus className="w-4 h-4 mr-2" /> Nouveau devis
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total",     count: devis.length,                                      color: "text-slate-900" },
          { label: "Envoyés",   count: devis.filter(d => d.statut === "ENVOYE").length,   color: "text-blue-600" },
          { label: "Acceptés",  count: devis.filter(d => d.statut === "ACCEPTE").length,  color: "text-emerald-600" },
          { label: "Convertis", count: devis.filter(d => d.statut === "CONVERTI").length, color: "text-purple-600" },
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
      ) : devis.length === 0 ? (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <FileEdit className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Aucun devis</h3>
            <p className="text-slate-400 text-center max-w-md mb-6">
              Créez votre premier devis pour envoyer une estimation à vos clients.
            </p>
            <Button onClick={() => setShowForm(true)} className="bg-slate-900 hover:bg-slate-700">
              <Plus className="w-4 h-4 mr-2" /> Créer un devis
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
                    <th key={h} className={`px-6 py-3.5 text-xs font-bold text-slate-400 uppercase tracking-wider ${h === "Montant TTC" ? "text-right" : h === "Actions" ? "text-center" : "text-left"}`}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {paginated.map(d => (
                  <tr key={d.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-6 py-4 font-mono font-semibold text-blue-600 text-xs">{d.numero}</td>

                    {/* ✅ Email du client depuis le map */}
                    <td className="px-6 py-4 text-slate-700 font-medium">
                      {clientMap[d.client_id] ?? (
                        <span className="text-slate-300 italic text-xs">Client #{d.client_id}</span>
                      )}
                    </td>

                    <td className="px-6 py-4"><StatusBadge statut={d.statut} /></td>

                    {/* ✅ Montant TTC calculé correctement */}
                    <td className="px-6 py-4 text-right font-semibold text-slate-900">
                      {getMontantTTC(d).toLocaleString("fr-TN", {
                        minimumFractionDigits: 3,
                        maximumFractionDigits: 3,
                      })} DT
                    </td>

                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {new Date(d.date_creation).toLocaleDateString("fr-FR")}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-1.5">
                        <button onClick={() => handleDownloadPdf(d.id)}
                          className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition">
                          <Download className="w-3 h-3" /> PDF
                        </button>
                        {d.statut === "BROUILLON" && (
                          <button onClick={() => handleAction(d.id, "envoyer")}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:border-slate-900 hover:text-slate-900 transition">
                            <Send className="w-3 h-3" /> Envoyer
                          </button>
                        )}
                        {d.statut === "ENVOYE" && (
                          <>
                            <button onClick={() => handleAction(d.id, "accepter")}
                              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-emerald-200 text-emerald-700 rounded-lg hover:bg-emerald-50 transition">
                              <CheckCircle className="w-3 h-3" /> Accepter
                            </button>
                            <button onClick={() => handleAction(d.id, "refuser")}
                              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition">
                              <XCircle className="w-3 h-3" /> Refuser
                            </button>
                          </>
                        )}
                        {d.statut === "ACCEPTE" && (
                          <button onClick={() => setConverting(d)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold bg-slate-900 text-white rounded-lg hover:bg-slate-700 transition">
                            <ArrowRight className="w-3 h-3" /> Convertir
                          </button>
                        )}
                        {(d.statut === "BROUILLON" || d.statut === "REFUSE") && (
                          <button onClick={() => handleDelete(d.id)}
                            className="w-7 h-7 flex items-center justify-center text-red-400 hover:bg-red-50 rounded-lg transition">
                            <Trash2 className="w-3.5 h-3.5" />
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
                <span className="text-xs text-slate-400">{devis.length} devis</span>
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

      {converting && (
        <ConversionModal devis={converting} onClose={() => setConverting(null)}
          onDone={() => { setConverting(null); fetchDevis(); }} />
      )}
    </div>
  );
}
