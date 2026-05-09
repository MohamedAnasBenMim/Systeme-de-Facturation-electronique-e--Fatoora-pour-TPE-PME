import { useState, useRef } from "react";
import {
  createProduit, updateProduit, uploadImage,
  Produit, Categorie, UniteMesure, ProduitCreate,
} from "../../../services/productService";
import { Button } from "../ui/button";
import { Input }  from "../ui/input";
import { Label }  from "../ui/label";

interface Props {
  produit?:    Produit | null;
  categories:  Categorie[];
  unites:      UniteMesure[];
  onClose:     () => void;
  onSaved:     () => void;
}

const EMPTY: ProduitCreate = {
  type: "PRODUIT", designation: "", reference: "", code_barre: "",
  description: "", marque: "", categorie_id: undefined, unite_id: undefined,
  prix_achat_ht: 0, prix_vente_ht: 0, taxe_id: "", groupe_taxe_id: "",
  is_stockable: true,
};

export function ProduitModal({ produit, categories, unites, onClose, onSaved }: Props) {
  const isEdit = !!produit;
  const [form,    setForm]    = useState<ProduitCreate>(
    produit ? {
      type:           produit.type,
      designation:    produit.designation,
      reference:      produit.reference || "",
      code_barre:     produit.code_barre || "",
      description:    produit.description || "",
      marque:         produit.marque || "",
      categorie_id:   produit.categorie?.id,
      unite_id:       produit.unite?.id,
      prix_achat_ht:  produit.prix_achat_ht,
      prix_vente_ht:  produit.prix_vente_ht,
      taxe_id:        produit.taxe_id || "",
      groupe_taxe_id: produit.groupe_taxe_id || "",
      is_stockable:   produit.is_stockable,
    } : EMPTY
  );
  const [saving,   setSaving]   = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [imgFile,  setImgFile]  = useState<File | null>(null);
  const [preview,  setPreview]  = useState<string | null>(produit?.image_url || null);
  const fileRef = useRef<HTMLInputElement>(null);

  const set = (k: keyof ProduitCreate, v: any) =>
    setForm((f) => ({ ...f, [k]: v }));

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setImgFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const handleSave = async () => {
    if (!form.designation) { setError("La désignation est obligatoire."); return; }
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        categorie_id:   form.categorie_id   || undefined,
        unite_id:       form.unite_id       || undefined,
        taxe_id:        form.taxe_id        || undefined,
        groupe_taxe_id: form.groupe_taxe_id || undefined,
        reference:      form.reference      || undefined,
      };

      let saved: Produit;
      if (isEdit && produit) {
        const { data } = await updateProduit(produit.id, payload);
        saved = data;
      } else {
        const { data } = await createProduit(payload);
        saved = data;
      }

      // Upload image si sélectionnée
      if (imgFile) {
        await uploadImage(saved.id, imgFile);
      }

      onSaved();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Erreur lors de l'enregistrement.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-xl">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEdit ? "Modifier l'article" : "Nouvel article"}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>

        <div className="p-6 space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">{error}</div>
          )}

          {/* Type */}
          <div className="flex gap-3">
            {(["PRODUIT", "SERVICE"] as const).map((t) => (
              <button
                key={t}
                onClick={() => set("type", t)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition ${
                  form.type === t
                    ? t === "SERVICE"
                      ? "border-purple-500 bg-purple-50 text-purple-700"
                      : "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 text-gray-500 hover:bg-gray-50"
                }`}
              >
                {t === "PRODUIT" ? "Produit physique" : "Service / Prestation"}
              </button>
            ))}
          </div>

          {/* Image */}
          <div
            onClick={() => fileRef.current?.click()}
            className="border-2 border-dashed border-gray-200 rounded-lg p-4 text-center cursor-pointer hover:border-blue-300 transition"
          >
            {preview ? (
              <img src={preview} alt="" className="h-24 mx-auto object-contain rounded" />
            ) : (
              <p className="text-sm text-gray-400">Cliquer pour ajouter une image (PNG, JPEG, WebP)</p>
            )}
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
          </div>

          {/* Désignation + Référence */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1 col-span-2">
              <Label>Désignation *</Label>
              <Input value={form.designation} onChange={(e) => set("designation", e.target.value)} placeholder="ex: PC Portable Dell XPS 13" />
            </div>
            <div className="space-y-1">
              <Label>Référence (SKU)</Label>
              <Input value={form.reference} onChange={(e) => set("reference", e.target.value)} placeholder="Auto-générée si vide" />
            </div>
            <div className="space-y-1">
              <Label>Code-barres (EAN)</Label>
              <Input value={form.code_barre} onChange={(e) => set("code_barre", e.target.value)} placeholder="Optionnel" />
            </div>
          </div>

          {/* Marque + Catégorie + Unité */}
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label>Marque</Label>
              <Input value={form.marque} onChange={(e) => set("marque", e.target.value)} placeholder="ex: Dell" />
            </div>
            <div className="space-y-1">
              <Label>Catégorie</Label>
              <select
                value={form.categorie_id || ""}
                onChange={(e) => set("categorie_id", e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
              >
                <option value="">Sans catégorie</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Unité</Label>
              <select
                value={form.unite_id || ""}
                onChange={(e) => set("unite_id", e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
              >
                <option value="">—</option>
                {unites.map((u) => <option key={u.id} value={u.id}>{u.nom} ({u.code})</option>)}
              </select>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1">
            <Label>Description (affichée sur les factures)</Label>
            <textarea
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none"
              placeholder="Description détaillée..."
            />
          </div>

          {/* Prix */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Prix d'achat HT (TND)</Label>
              <Input
                type="number" min={0} step={0.001}
                value={form.prix_achat_ht}
                onChange={(e) => set("prix_achat_ht", parseFloat(e.target.value) || 0)}
              />
            </div>
            <div className="space-y-1">
              <Label>Prix de vente HT (TND) *</Label>
              <Input
                type="number" min={0} step={0.001}
                value={form.prix_vente_ht}
                onChange={(e) => set("prix_vente_ht", parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>

          {/* Options */}
          <div className="flex gap-6">
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_stockable}
                onChange={(e) => set("is_stockable", e.target.checked)}
              />
              Gérer le stock pour cet article
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 px-6 py-4 border-t border-gray-100">
          <Button onClick={handleSave} disabled={saving} className="flex-1">
            {saving ? "Enregistrement..." : isEdit ? "Mettre à jour" : "Créer l'article"}
          </Button>
          <Button variant="outline" onClick={onClose} className="flex-1">Annuler</Button>
        </div>
      </div>
    </div>
  );
}