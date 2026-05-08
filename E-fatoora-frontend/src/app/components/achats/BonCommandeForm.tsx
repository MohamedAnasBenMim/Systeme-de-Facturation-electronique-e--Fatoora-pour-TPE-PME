import { useState } from "react";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent } from "../ui/card";
import type { BonCommande, LigneBonCommande, Fournisseur } from "../../../services/achatsService";

interface Props {
  fournisseurs: Fournisseur[];  // passé depuis la page parent (déjà chargés)
  onCancel: () => void;
  onSubmit: (data: Partial<BonCommande>) => Promise<void>;
}

//  Aligné sur LigneBonCommande du vrai modèle
const emptyLigne = (): LigneBonCommande => ({
  product_id:             0,
  designation:            "",
  reference_fournisseur:  "",
  quantite_commandee:     1,
  prix_unitaire:          0,
  montant_ligne:          0,
});

export function BonCommandeForm({ fournisseurs, onCancel, onSubmit }: Props) {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    fournisseur_id:           0,
    date_livraison_attendue:  "",   // ✅ date_livraison_attendue
    date_echeance_paiement:   "",   // ✅ date_echeance_paiement
    notes:                    "",
  });
  const [lignes, setLignes] = useState<LigneBonCommande[]>([emptyLigne()]);

  const handleFournisseurChange = (id: number) => {
    const f = fournisseurs.find(f => f.id === id);
    setForm(prev => ({ ...prev, fournisseur_id: id }));
  };

  // ✅ montant_ligne = quantite_commandee × prix_unitaire (pas de TVA dans ce modèle)
  const updateLigne = (idx: number, key: keyof LigneBonCommande, val: any) => {
    setLignes(prev => {
      const next = [...prev];
      const ligne = { ...next[idx], [key]: val };
      if (key === "quantite_commandee" || key === "prix_unitaire") {
        ligne.montant_ligne = ligne.quantite_commandee * ligne.prix_unitaire;
      }
      next[idx] = ligne;
      return next;
    });
  };

  const addLigne    = () => setLignes(prev => [...prev, emptyLigne()]);
  const removeLigne = (idx: number) => setLignes(prev => prev.filter((_, i) => i !== idx));

  // ✅ total_ht et tva calculés pour le BC
  const total_ht  = lignes.reduce((s, l) => s + l.montant_ligne, 0);
  const tva       = total_ht * 0.19;
  const timbre    = 1.0;  // timbre fiscal fixe
  const total_ttc = total_ht + tva + timbre;

  const handleSubmit = async () => {
    if (!form.fournisseur_id)                   return alert("Sélectionnez un fournisseur.");
    if (lignes.length === 0)                    return alert("Ajoutez au moins une ligne.");
    if (lignes.some(l => !l.designation.trim())) return alert("Toutes les lignes doivent avoir une désignation.");
    if (lignes.some(l => l.quantite_commandee <= 0 || l.prix_unitaire <= 0))
      return alert("Quantité et prix unitaire doivent être > 0.");

    setLoading(true);
    try {
      await onSubmit({
        ...form,
        total_ht,
        tva,
        timbre_fiscal: timbre,
        total_ttc,
        // ✅ lignes avec quantite_receptionnable = quantite_commandee à la création
        lignes: lignes.map(l => ({ ...l, quantite_receptionnable: l.quantite_commandee, quantite_receptionnee: 0 })),
      });
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur");
    } finally {
      setLoading(false);
    }
  };

  const inputCls = "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900";
  const Field = ({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) => (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {children}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={onCancel} className="p-2 hover:bg-slate-100 rounded-lg transition">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nouveau bon de commande</h1>
          <p className="text-gray-500 text-sm mt-0.5">Le numéro BC sera généré automatiquement</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* En-tête */}
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-6">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Informations générales</h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-1">
                <Field label="Fournisseur" required>
                  <select value={form.fournisseur_id} onChange={e => handleFournisseurChange(parseInt(e.target.value))} className={inputCls}>
                    <option value={0}>— Sélectionner —</option>
                    {fournisseurs.map(f => (
                      // ✅ f.nom
                      <option key={f.id} value={f.id}>{f.nom}</option>
                    ))}
                  </select>
                </Field>
              </div>
              <Field label="Date de livraison prévue">
                {/* ✅ date_livraison_attendue */}
                <input type="date" value={form.date_livraison_attendue}
                  onChange={e => setForm(f => ({ ...f, date_livraison_attendue: e.target.value }))}
                  className={inputCls} />
              </Field>
              <Field label="Date d'échéance paiement">
                {/* ✅ date_echeance_paiement */}
                <input type="date" value={form.date_echeance_paiement}
                  onChange={e => setForm(f => ({ ...f, date_echeance_paiement: e.target.value }))}
                  className={inputCls} />
              </Field>
              <div className="col-span-3">
                <Field label="Notes">
                  <input value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                    className={inputCls} placeholder="Notes internes..." />
                </Field>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lignes */}
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Lignes de commande</h2>
              <button onClick={addLigne} className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:border-slate-900 transition">
                <Plus className="w-3 h-3" /> Ajouter une ligne
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    {["Désignation *", "Réf. fournisseur", "Qté *", "Prix unitaire *", "Montant ligne", ""].map(h => (
                      <th key={h} className="px-2 py-2 text-xs font-bold text-slate-400 text-left whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {lignes.map((ligne, idx) => (
                    <tr key={idx} className="group">
                      <td className="px-2 py-2">
                        {/* ✅ designation */}
                        <input value={ligne.designation}
                          onChange={e => updateLigne(idx, "designation", e.target.value)}
                          placeholder="Désignation du produit"
                          className="w-56 border border-slate-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-900" />
                      </td>
                      <td className="px-2 py-2">
                        {/* ✅ reference_fournisseur */}
                        <input value={ligne.reference_fournisseur ?? ""}
                          onChange={e => updateLigne(idx, "reference_fournisseur", e.target.value)}
                          placeholder="REF-FOUR"
                          className="w-28 border border-slate-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-900" />
                      </td>
                      <td className="px-2 py-2">
                        {/* ✅ quantite_commandee */}
                        <input type="number" min={1} step={1}
                          value={ligne.quantite_commandee}
                          onChange={e => updateLigne(idx, "quantite_commandee", parseInt(e.target.value) || 0)}
                          className="w-20 border border-slate-200 rounded px-2 py-1.5 text-sm text-right focus:outline-none focus:ring-1 focus:ring-slate-900" />
                      </td>
                      <td className="px-2 py-2">
                        {/* ✅ prix_unitaire */}
                        <input type="number" min={0} step={0.001}
                          value={ligne.prix_unitaire}
                          onChange={e => updateLigne(idx, "prix_unitaire", parseFloat(e.target.value) || 0)}
                          className="w-28 border border-slate-200 rounded px-2 py-1.5 text-sm text-right focus:outline-none focus:ring-1 focus:ring-slate-900" />
                      </td>
                      <td className="px-2 py-2 text-right font-semibold text-slate-900 whitespace-nowrap">
                        {/* ✅ montant_ligne */}
                        {ligne.montant_ligne.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                      </td>
                      <td className="px-2 py-2">
                        {lignes.length > 1 && (
                          <button onClick={() => removeLigne(idx)} className="p-1 text-red-400 hover:bg-red-50 rounded transition opacity-0 group-hover:opacity-100">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Totaux */}
            <div className="flex justify-end mt-4 pt-4 border-t border-slate-100">
              <div className="space-y-1 text-sm min-w-64">
                <div className="flex justify-between text-slate-500">
                  <span>Total HT</span>
                  <span className="font-medium">{total_ht.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>TVA (19%)</span>
                  <span className="font-medium">{tva.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Timbre fiscal</span>
                  <span className="font-medium">{timbre.toFixed(3)} DT</span>
                </div>
                <div className="flex justify-between font-bold text-slate-900 text-base border-t border-slate-200 pt-1">
                  <span>Total TTC</span>
                  <span>{total_ttc.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onCancel}>Annuler</Button>
          <Button onClick={handleSubmit} disabled={loading} className="bg-slate-900 hover:bg-slate-700">
            {loading ? "Création..." : "Créer en brouillon"}
          </Button>
        </div>
      </div>
    </div>
  );
}