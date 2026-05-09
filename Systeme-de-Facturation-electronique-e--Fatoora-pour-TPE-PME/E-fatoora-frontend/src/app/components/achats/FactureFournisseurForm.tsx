import { useEffect, useState } from "react";
import { ArrowLeft, Plus, Trash2, AlertTriangle } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent } from "../ui/card";
import {
  fournisseurService,
  bonCommandeService,
  type Fournisseur,
  type BonCommande,
  type FactureFournisseur,
  type LigneFacture,
} from "../../../services/achatsService";

interface Props {
  onCancel: () => void;
  onSubmit: (data: Partial<FactureFournisseur>) => Promise<void>;
}

const emptyLigne = (): LigneFacture => ({
  product_id: 0,
  designation: "",
  quantite_facturee: 1,
  prix_unitaire: 0,
  montant_ligne: 0,
});

export function FactureFournisseurForm({ onCancel, onSubmit }: Props) {
  const [fournisseurs, setFournisseurs]   = useState<Fournisseur[]>([]);
  const [bonsCommande, setBonsCommande]   = useState<BonCommande[]>([]);
  const [bcFiltrees, setBcFiltrees]       = useState<BonCommande[]>([]);
  const [selectedFour, setSelectedFour]  = useState<Fournisseur | null>(null);
  const [selectedBC, setSelectedBC]      = useState<BonCommande | null>(null);
  const [loading, setLoading]            = useState(false);
  const [loadingData, setLoadingData]    = useState(true);

  const [form, setForm] = useState({
    fournisseur_id:                       0,
    bon_commande_id:                      undefined as number | undefined,
    // ✅ numero_facture — numéro que le fournisseur t'a envoyé
    numero_facture:                       "",
    date_facture:                         new Date().toISOString().split("T")[0],
    date_echeance:                        "",
    reference_bon_commande_fournisseur:   "",
    numero_bon_livraison_fournisseur:     "",
    notes:                                "",
  });

  const [lignes, setLignes] = useState<LigneFacture[]>([emptyLigne()]);

  useEffect(() => {
    const load = async () => {
      try {
        setLoadingData(true);
        const [fours, bcs] = await Promise.all([
          fournisseurService.getAll(true),
          bonCommandeService.getAll(),
        ]);
        setFournisseurs(fours);
        // On ne propose que les BC confirmés ou livrés (réception faite)
        setBonsCommande(bcs.filter(bc => ["CONFIRMEE", "LIVREE", "DIFFERENCIEE"].includes(bc.statut)));
      } catch (e) {
        console.error("Erreur chargement données", e);
      } finally {
        setLoadingData(false);
      }
    };
    load();
  }, []);

  // Quand on change de fournisseur → filtrer les BC correspondants
  const handleFournisseurChange = (id: number) => {
    const f = fournisseurs.find(f => f.id === id) ?? null;
    setSelectedFour(f);
    setSelectedBC(null);
    setForm(prev => ({
      ...prev,
      fournisseur_id: id,
      bon_commande_id: undefined,
      // Auto-calcul échéance selon délai fournisseur
      date_echeance: f
        ? computeEcheance(prev.date_facture, f.delai_paiement_jours)
        : prev.date_echeance,
    }));
    // Filtrer les BC du fournisseur sélectionné
    setBcFiltrees(bonsCommande.filter(bc => bc.fournisseur_id === id));
    setLignes([emptyLigne()]);
  };

  // Quand on sélectionne un BC → pré-remplir les lignes depuis ses lignes
  const handleBCChange = (id: number) => {
    const bc = bcFiltrees.find(bc => bc.id === id) ?? null;
    setSelectedBC(bc);
    setForm(prev => ({ ...prev, bon_commande_id: id }));
    if (bc && bc.lignes.length > 0) {
      // Pré-remplir les lignes de la facture depuis les lignes du BC
      setLignes(bc.lignes.map(l => ({
        ligne_bc_id:       l.id,
        product_id:        l.product_id,
        designation:       l.designation,
        quantite_facturee: l.quantite_commandee,
        prix_unitaire:     l.prix_unitaire,
        montant_ligne:     l.montant_ligne,
      })));
    }
  };

  const handleDateFactureChange = (date: string) => {
    setForm(prev => ({
      ...prev,
      date_facture: date,
      date_echeance: selectedFour
        ? computeEcheance(date, selectedFour.delai_paiement_jours)
        : prev.date_echeance,
    }));
  };

  const computeEcheance = (dateFacture: string, delaiJours: number): string => {
    const d = new Date(dateFacture);
    d.setDate(d.getDate() + delaiJours);
    return d.toISOString().split("T")[0];
  };

  const updateLigne = (idx: number, key: keyof LigneFacture, val: any) => {
    setLignes(prev => {
      const next = [...prev];
      const ligne = { ...next[idx], [key]: val };
      // Recalcul automatique montant_ligne
      if (key === "quantite_facturee" || key === "prix_unitaire") {
        ligne.montant_ligne = ligne.quantite_facturee * ligne.prix_unitaire;
      }
      next[idx] = ligne;
      return next;
    });
  };

  const addLigne    = () => setLignes(prev => [...prev, emptyLigne()]);
  const removeLigne = (idx: number) => setLignes(prev => prev.filter((_, i) => i !== idx));

  // Totaux
  const total_ht  = lignes.reduce((s, l) => s + l.montant_ligne, 0);
  // TVA simplifiée — dans ton modèle il n'y a pas de taux TVA par ligne
  // mais on peut l'ajouter; pour l'instant on prend 19% du total
  const total_tva = total_ht * 0.19;
  const total_ttc = total_ht + total_tva;

  const handleSubmit = async () => {
    if (!form.fournisseur_id)  return alert("Veuillez sélectionner un fournisseur.");
    if (!form.numero_facture.trim()) return alert("Veuillez saisir le numéro de facture fournisseur.");
    if (!form.date_facture)    return alert("Veuillez saisir la date de facture.");
    if (lignes.length === 0)   return alert("Veuillez ajouter au moins une ligne.");
    if (lignes.some(l => !l.designation.trim())) return alert("Toutes les lignes doivent avoir une désignation.");
    if (lignes.some(l => l.quantite_facturee <= 0 || l.prix_unitaire <= 0)) {
      return alert("Quantité et prix unitaire doivent être supérieurs à 0.");
    }

    setLoading(true);
    try {
      await onSubmit({
        ...form,
        total_ht,
        total_tva,
        total_ttc,
        total_ttc_net: total_ttc,  // sera ajusté après avoirs
        lignes,
      });
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur lors de la création");
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

  if (loadingData) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400">Chargement des données...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center gap-4">
        <button onClick={onCancel} className="p-2 hover:bg-slate-100 rounded-lg transition">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Saisir une facture fournisseur</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Rapprochement automatique avec le bon de commande
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Section 1 — Identification */}
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-6">
            <h2 className="text-sm font-bold text-slate-700 border-b border-slate-100 pb-2 mb-4">
              Identification de la facture
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-1">
                <Field label="Fournisseur" required>
                  <select
                    value={form.fournisseur_id}
                    onChange={e => handleFournisseurChange(parseInt(e.target.value))}
                    className={inputCls}
                  >
                    <option value={0}>— Sélectionner —</option>
                    {fournisseurs.map(f => (
                      // ✅ f.nom — vrai champ du modèle
                      <option key={f.id} value={f.id}>{f.nom}</option>
                    ))}
                  </select>
                </Field>
              </div>

              <div className="col-span-2">
                <Field label="Bon de commande associé">
                  <select
                    value={form.bon_commande_id ?? ""}
                    onChange={e => e.target.value ? handleBCChange(parseInt(e.target.value)) : null}
                    disabled={!form.fournisseur_id}
                    className={inputCls + " disabled:opacity-50 disabled:cursor-not-allowed"}
                  >
                    <option value="">— Sélectionner un BC (optionnel) —</option>
                    {bcFiltrees.map(bc => (
                      // ✅ bc.numero_bc — vrai champ du modèle
                      <option key={bc.id} value={bc.id}>
                        {bc.numero_bc} — {bc.total_ttc?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                      </option>
                    ))}
                  </select>
                  {form.fournisseur_id > 0 && bcFiltrees.length === 0 && (
                    <p className="text-xs text-amber-600 mt-1">
                      Aucun bon de commande confirmé pour ce fournisseur
                    </p>
                  )}
                </Field>
              </div>

              {/* ✅ numero_facture — numéro du fournisseur */}
              <Field label="N° de facture fournisseur" required>
                <input
                  value={form.numero_facture}
                  onChange={e => setForm(f => ({ ...f, numero_facture: e.target.value }))}
                  className={inputCls}
                  placeholder="Ex: FAC-2024-0042"
                />
              </Field>

              <Field label="Date de facture" required>
                <input
                  type="date"
                  value={form.date_facture}
                  onChange={e => handleDateFactureChange(e.target.value)}
                  className={inputCls}
                />
              </Field>

              <Field label="Date d'échéance">
                <input
                  type="date"
                  value={form.date_echeance}
                  min={form.date_facture}
                  onChange={e => setForm(f => ({ ...f, date_echeance: e.target.value }))}
                  className={inputCls}
                />
                {selectedFour && (
                  <p className="text-xs text-slate-400 mt-1">
                    Calculée automatiquement : {selectedFour.delai_paiement_jours} jours
                  </p>
                )}
              </Field>

              <Field label="Réf. BC du fournisseur">
                <input
                  value={form.reference_bon_commande_fournisseur}
                  onChange={e => setForm(f => ({ ...f, reference_bon_commande_fournisseur: e.target.value }))}
                  className={inputCls}
                  placeholder="Ex: BC-FOUR-001"
                />
              </Field>

              <Field label="N° bon de livraison fournisseur">
                <input
                  value={form.numero_bon_livraison_fournisseur}
                  onChange={e => setForm(f => ({ ...f, numero_bon_livraison_fournisseur: e.target.value }))}
                  className={inputCls}
                  placeholder="Ex: BL-2024-001"
                />
              </Field>

              <Field label="Notes">
                <input
                  value={form.notes}
                  onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                  className={inputCls}
                  placeholder="Observations..."
                />
              </Field>
            </div>
          </CardContent>
        </Card>

        {/* Alerte rapprochement si BC sélectionné */}
        {selectedBC && (
          <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <AlertTriangle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-blue-700">Rapprochement automatique activé</p>
              <p className="text-xs text-blue-600 mt-0.5">
                Les montants de cette facture seront comparés au BC {selectedBC.numero_bc} ({selectedBC.total_ttc?.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT TTC).
                Si l'écart dépasse le seuil de tolérance du fournisseur ({selectedFour?.seuil_tolerance_prix}%), la facture sera bloquée en litige.
              </p>
            </div>
          </div>
        )}

        {/* Section 2 — Lignes de facture */}
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-slate-700">Lignes de la facture</h2>
              <button
                onClick={addLigne}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:border-slate-900 transition"
              >
                <Plus className="w-3 h-3" /> Ajouter une ligne
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    {["Désignation *", "Réf. BC", "Qté facturée *", "Prix unitaire *", "Montant ligne", ""].map(h => (
                      <th key={h} className="px-2 py-2 text-xs font-bold text-slate-400 text-left whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {lignes.map((ligne, idx) => (
                    <tr key={idx} className="group">
                      <td className="px-2 py-2">
                        <input
                          value={ligne.designation}
                          onChange={e => updateLigne(idx, "designation", e.target.value)}
                          placeholder="Description du produit/service"
                          className="w-64 border border-slate-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-900"
                        />
                      </td>
                      <td className="px-2 py-2">
                        {/* Lien vers ligne du BC */}
                        {selectedBC ? (
                          <select
                            value={ligne.ligne_bc_id ?? ""}
                            onChange={e => {
                              const bcLigne = selectedBC.lignes.find(l => l.id === parseInt(e.target.value));
                              if (bcLigne) {
                                updateLigne(idx, "ligne_bc_id", bcLigne.id);
                                updateLigne(idx, "product_id", bcLigne.product_id);
                                updateLigne(idx, "designation", bcLigne.designation);
                                updateLigne(idx, "prix_unitaire", bcLigne.prix_unitaire);
                                updateLigne(idx, "quantite_facturee", bcLigne.quantite_commandee);
                                updateLigne(idx, "montant_ligne", bcLigne.montant_ligne);
                              }
                            }}
                            className="w-36 border border-slate-200 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-slate-900"
                          >
                            <option value="">— Aucun —</option>
                            {selectedBC.lignes.map(l => (
                              <option key={l.id} value={l.id}>{l.designation}</option>
                            ))}
                          </select>
                        ) : (
                          <span className="text-xs text-slate-300 italic">Sélect. un BC</span>
                        )}
                      </td>
                      <td className="px-2 py-2">
                        <input
                          type="number" min={1} step={1}
                          value={ligne.quantite_facturee}
                          onChange={e => updateLigne(idx, "quantite_facturee", parseInt(e.target.value) || 0)}
                          className="w-24 border border-slate-200 rounded px-2 py-1.5 text-sm text-right focus:outline-none focus:ring-1 focus:ring-slate-900"
                        />
                      </td>
                      <td className="px-2 py-2">
                        <input
                          type="number" min={0} step={0.001}
                          value={ligne.prix_unitaire}
                          onChange={e => updateLigne(idx, "prix_unitaire", parseFloat(e.target.value) || 0)}
                          className="w-28 border border-slate-200 rounded px-2 py-1.5 text-sm text-right focus:outline-none focus:ring-1 focus:ring-slate-900"
                        />
                      </td>
                      <td className="px-2 py-2 text-right font-semibold text-slate-900 whitespace-nowrap">
                        {ligne.montant_ligne.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                      </td>
                      <td className="px-2 py-2">
                        {lignes.length > 1 && (
                          <button
                            onClick={() => removeLigne(idx)}
                            className="p-1 text-red-400 hover:bg-red-50 rounded transition opacity-0 group-hover:opacity-100"
                          >
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
            <div className="flex justify-end mt-6 pt-4 border-t border-slate-100">
              <div className="space-y-1.5 text-sm min-w-72">
                <div className="flex justify-between text-slate-500">
                  <span>Total HT</span>
                  <span className="font-medium">{total_ht.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>TVA (19%)</span>
                  <span className="font-medium">{total_tva.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT</span>
                </div>
                <div className="flex justify-between font-bold text-slate-900 text-base border-t border-slate-200 pt-1.5 mt-1.5">
                  <span>Total TTC</span>
                  <span>{total_ttc.toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT</span>
                </div>
                {selectedBC && (
                  <div className={`flex justify-between text-xs pt-1 ${
                    Math.abs(total_ttc - selectedBC.total_ttc) / selectedBC.total_ttc * 100 > (selectedFour?.seuil_tolerance_prix ?? 5)
                      ? "text-red-500 font-semibold"
                      : "text-emerald-600"
                  }`}>
                    <span>Écart vs BC ({selectedBC.numero_bc})</span>
                    <span>
                      {(total_ttc - selectedBC.total_ttc).toLocaleString("fr-TN", { minimumFractionDigits: 3 })} DT
                      ({Math.abs((total_ttc - selectedBC.total_ttc) / selectedBC.total_ttc * 100).toFixed(1)}%)
                    </span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onCancel}>Annuler</Button>
          <Button onClick={handleSubmit} disabled={loading} className="bg-slate-900 hover:bg-slate-700">
            {loading ? "Enregistrement..." : "Enregistrer la facture"}
          </Button>
        </div>
      </div>
    </div>
  );
}