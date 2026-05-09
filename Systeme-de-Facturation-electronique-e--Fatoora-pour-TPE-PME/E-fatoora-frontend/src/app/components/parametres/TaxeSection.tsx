// src/components/parametres/TaxesSection.tsx
import { useEffect, useState } from "react";
import { getTaxes, createTaxe, updateTaxe, deleteTaxe, getGroupes, createGroupe, updateGroupe, deleteGroupe, Taxe, GroupeTaxe, TaxeCreate, GroupeTaxeCreate } from "../../../services/taxeService";
import { Button }  from "../ui/button";
import { Input }   from "../ui/input";
import { Label }   from "../ui/label";

// ── Taxes prédéfinies (raccourcis) ────────────────────────
const TAXES_PREDEFINIES: TaxeCreate[] = [
  { nom: "TVA",            code: "TVA_19",   taux: 19,  description: "Taxe sur la valeur ajoutée 19%" },
  { nom: "TVA réduite",    code: "TVA_13",   taux: 13,  description: "Taxe sur la valeur ajoutée 13%" },
  { nom: "TVA super-réduite", code: "TVA_7", taux: 7,   description: "Taxe sur la valeur ajoutée 7%"  },
  { nom: "FODEC",          code: "FODEC_1",  taux: 1,   description: "Fonds de développement de la compétitivité" },
  { nom: "Droit de timbre",code: "TIMBRE",   taux: 0.6, description: "Droit de timbre fiscal"          },
];

export function TaxesSection() {
  const [taxes,   setTaxes]   = useState<Taxe[]>([]);
  const [groupes, setGroupes] = useState<GroupeTaxe[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"taxes" | "groupes">("taxes");

  // Formulaire taxe
  const [form, setForm]         = useState<TaxeCreate>({ nom: "", code: "", taux: 0, description: "", est_active: true, est_defaut: false });
  const [editId, setEditId]     = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving]     = useState(false);
  const [error, setError]       = useState<string | null>(null);

  // Formulaire groupe
  const [gForm, setGForm]         = useState<GroupeTaxeCreate>({ nom: "", description: "", taxe_ids: [] });
  const [showGForm, setShowGForm] = useState(false);
  const [gSaving, setGSaving]     = useState(false);

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    setLoading(true);
    const [t, g] = await Promise.all([getTaxes(), getGroupes()]);
    setTaxes(t.data);
    setGroupes(g.data);
    setLoading(false);
  };
  useEffect(() => {
  // ✅ Affiche le contenu de ton token décodé
  const token = localStorage.getItem("access_token");
  if (token) {
    const payload = JSON.parse(atob(token.split(".")[1]));
    console.log("Token payload:", payload);  // vérifie que entreprise_id est présent
  }
  loadAll();
 }, []);

  // ── CRUD Taxe ──────────────────────────────────────────
  const handleSaveTaxe = async () => {
    if (!form.nom || !form.code || form.taux < 0) {
      setError("Veuillez remplir tous les champs obligatoires.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (editId) {
        await updateTaxe(editId, form);
      } else {
        await createTaxe(form);
      }
      await loadAll();
      resetTaxeForm();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Erreur lors de l'enregistrement.");
    } finally {
      setSaving(false);
    }
  };

  const handleEditTaxe = (t: Taxe) => {
    setForm({ nom: t.nom, code: t.code, taux: t.taux, description: t.description, est_active: t.est_active, est_defaut: t.est_defaut });
    setEditId(t.id);
    setShowForm(true);
  };

  const handleDeleteTaxe = async (id: string) => {
    if (!confirm("Supprimer cette taxe ?")) return;
    await deleteTaxe(id);
    await loadAll();
  };

  const handlePredefinie = (t: TaxeCreate) => {
    setForm(t);
    setEditId(null);
    setShowForm(true);
  };

  const resetTaxeForm = () => {
    setForm({ nom: "", code: "", taux: 0, description: "", est_active: true, est_defaut: false });
    setEditId(null);
    setShowForm(false);
  };

  // ── CRUD Groupe ────────────────────────────────────────
  const handleSaveGroupe = async () => {
    if (!gForm.nom || gForm.taxe_ids.length === 0) {
      setError("Nom et au moins une taxe sont requis.");
      return;
    }
    setGSaving(true);
    setError(null);
    try {
      await createGroupe(gForm);
      await loadAll();
      setGForm({ nom: "", description: "", taxe_ids: [] });
      setShowGForm(false);
    } catch (e: any) {
      setError(e.response?.data?.detail || "Erreur lors de la création du groupe.");
    } finally {
      setGSaving(false);
    }
  };

  const toggleTaxeInGroupe = (id: string) => {
    setGForm((prev) => ({
      ...prev,
      taxe_ids: prev.taxe_ids.includes(id)
        ? prev.taxe_ids.filter((x) => x !== id)
        : [...prev.taxe_ids, id],
    }));
  };

  const handleDeleteGroupe = async (id: string) => {
    if (!confirm("Supprimer ce groupe ?")) return;
    await deleteGroupe(id);
    await loadAll();
  };

  if (loading) return <p className="text-gray-500 text-sm">Chargement...</p>;

  return (
    <div className="space-y-6">
      {/* Sous-tabs */}
      <div className="flex gap-4 border-b border-gray-100">
        {(["taxes", "groupes"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === t ? "border-blue-500 text-blue-600" : "border-transparent text-gray-400 hover:text-gray-600"
            }`}
          >
            {t === "taxes" ? "Référentiel des taxes" : "Groupes de taxes"}
          </button>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
          {error}
        </div>
      )}

      {/* ── Onglet TAXES ── */}
      {activeTab === "taxes" && (
        <div className="space-y-4">

          {/* Taxes prédéfinies */}
          <div>
            <p className="text-sm text-gray-500 mb-2">Ajouter rapidement une taxe standard :</p>
            <div className="flex flex-wrap gap-2">
              {TAXES_PREDEFINIES.map((t) => (
                <button
                  key={t.code}
                  onClick={() => handlePredefinie(t)}
                  className="px-3 py-1 text-xs border border-blue-200 text-blue-700 rounded-full hover:bg-blue-50 transition"
                >
                  + {t.nom} ({t.taux}%)
                </button>
              ))}
            </div>
          </div>

          {/* Bouton nouvelle taxe */}
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-medium text-gray-700">Taxes configurées</h2>
            <Button onClick={() => { resetTaxeForm(); setShowForm(true); }} className="text-sm">
              + Nouvelle taxe
            </Button>
          </div>

          {/* Formulaire taxe */}
          {showForm && (
            <div className="border border-gray-200 rounded-lg p-4 space-y-3 bg-gray-50">
              <h3 className="text-sm font-medium text-gray-700">
                {editId ? "Modifier la taxe" : "Nouvelle taxe"}
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Nom *</Label>
                  <Input placeholder="ex: TVA" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} />
                </div>
                <div className="space-y-1">
                  <Label>Code *</Label>
                  <Input placeholder="ex: TVA_19" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} />
                </div>
                <div className="space-y-1">
                  <Label>Taux (%) *</Label>
                  <Input type="number" min={0} max={100} step={0.1} value={form.taux} onChange={(e) => setForm({ ...form, taux: parseFloat(e.target.value) })} />
                </div>
                <div className="space-y-1">
                  <Label>Description</Label>
                  <Input placeholder="Optionnel" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                </div>
              </div>
              <div className="flex gap-4 text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.est_active} onChange={(e) => setForm({ ...form, est_active: e.target.checked })} />
                  Active
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.est_defaut} onChange={(e) => setForm({ ...form, est_defaut: e.target.checked })} />
                  Appliquée par défaut
                </label>
              </div>
              <div className="flex gap-2 pt-1">
                <Button onClick={handleSaveTaxe} disabled={saving}>
                  {saving ? "Enregistrement..." : editId ? "Modifier" : "Créer"}
                </Button>
                <Button variant="outline" onClick={resetTaxeForm}>Annuler</Button>
              </div>
            </div>
          )}

          {/* Liste des taxes */}
          {taxes.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">Aucune taxe configurée.</p>
          ) : (
            <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden">
              {taxes.map((t) => (
                <div key={t.id} className="flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{t.code}</span>
                    <div>
                      <p className="text-sm font-medium text-gray-800">{t.nom}</p>
                      {t.description && <p className="text-xs text-gray-400">{t.description}</p>}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-blue-600">{t.taux}%</span>
                    {t.est_defaut && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Défaut</span>}
                    {!t.est_active && <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">Inactive</span>}
                    <button onClick={() => handleEditTaxe(t)} className="text-xs text-blue-500 hover:underline">Modifier</button>
                    <button onClick={() => handleDeleteTaxe(t.id)} className="text-xs text-red-500 hover:underline">Supprimer</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Onglet GROUPES ── */}
      {activeTab === "groupes" && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-medium text-gray-700">Groupes de taxes</h2>
            <Button onClick={() => setShowGForm(true)} className="text-sm">+ Nouveau groupe</Button>
          </div>

          {/* Formulaire groupe */}
          {showGForm && (
            <div className="border border-gray-200 rounded-lg p-4 space-y-3 bg-gray-50">
              <h3 className="text-sm font-medium text-gray-700">Nouveau groupe</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Nom du groupe *</Label>
                  <Input placeholder="ex: TVA + FODEC" value={gForm.nom} onChange={(e) => setGForm({ ...gForm, nom: e.target.value })} />
                </div>
                <div className="space-y-1">
                  <Label>Description</Label>
                  <Input placeholder="Optionnel" value={gForm.description} onChange={(e) => setGForm({ ...gForm, description: e.target.value })} />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Sélectionner les taxes à combiner *</Label>
                {taxes.length === 0 ? (
                  <p className="text-xs text-gray-400">Aucune taxe disponible — créez d'abord des taxes.</p>
                ) : (
                  <div className="flex flex-wrap gap-2 mt-1">
                    {taxes.map((t) => (
                      <label key={t.id} className={`flex items-center gap-1.5 px-3 py-1.5 border rounded-lg cursor-pointer text-sm transition ${
                        gForm.taxe_ids.includes(t.id)
                          ? "border-blue-500 bg-blue-50 text-blue-700"
                          : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                      }`}>
                        <input
                          type="checkbox"
                          className="hidden"
                          checked={gForm.taxe_ids.includes(t.id)}
                          onChange={() => toggleTaxeInGroupe(t.id)}
                        />
                        {t.nom} ({t.taux}%)
                      </label>
                    ))}
                  </div>
                )}
                {gForm.taxe_ids.length > 0 && (
                  <p className="text-xs text-blue-600 mt-1">
                    Total : {taxes.filter((t) => gForm.taxe_ids.includes(t.id)).reduce((s, t) => s + t.taux, 0).toFixed(2)}%
                  </p>
                )}
              </div>
              <div className="flex gap-2 pt-1">
                <Button onClick={handleSaveGroupe} disabled={gSaving}>
                  {gSaving ? "Création..." : "Créer le groupe"}
                </Button>
                <Button variant="outline" onClick={() => { setShowGForm(false); setGForm({ nom: "", description: "", taxe_ids: [] }); }}>
                  Annuler
                </Button>
              </div>
            </div>
          )}

          {/* Liste des groupes */}
          {groupes.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">Aucun groupe configuré.</p>
          ) : (
            <div className="space-y-3">
              {groupes.map((g) => (
                <div key={g.id} className="border border-gray-200 rounded-lg p-4 bg-white space-y-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{g.nom}</p>
                      {g.description && <p className="text-xs text-gray-400">{g.description}</p>}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-blue-600">Total : {g.taux_total.toFixed(2)}%</span>
                      <button onClick={() => handleDeleteGroupe(g.id)} className="text-xs text-red-500 hover:underline">Supprimer</button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {g.taxes.map((t) => (
                      <span key={t.id} className="text-xs bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded-full">
                        {t.nom} {t.taux}%
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}