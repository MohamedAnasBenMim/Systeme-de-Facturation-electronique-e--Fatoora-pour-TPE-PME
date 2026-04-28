// src/components/parametres/CachetSection.tsx
import { useEffect, useRef, useState } from "react";
import { getCachet, getCachetImageUrl, uploadCachet, deleteCachet } from "../../../services/cachetService";
import { Button } from "../ui/button";
import { Input }  from "../ui/input";
import { Label }  from "../ui/label";

export function CachetSection() {
  const [cachet,   setCachet]   = useState<Cachet | null>(null);
  const [loading,  setLoading]  = useState(true);
  const [saving,   setSaving]   = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [success,  setSuccess]  = useState<string | null>(null);
  const [preview,  setPreview]  = useState<string | null>(null);
  const [file,     setFile]     = useState<File | null>(null);
  const [nom,      setNom]      = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadCachet(); }, []);

  const loadCachet = async () => {
    setLoading(true);
    try {
      const { data } = await getCachet();
      setCachet(data);
    } catch {
      setCachet(null); // pas encore de cachet
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;

    // Validation côté client
    if (!["image/png", "image/jpeg", "image/svg+xml"].includes(f.type)) {
      setError("Format non supporté. Utilisez PNG, JPEG ou SVG.");
      return;
    }
    if (f.size > 2 * 1024 * 1024) {
      setError("Fichier trop volumineux. Maximum 2 MB.");
      return;
    }

    setError(null);
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const handleUpload = async () => {
    if (!file) { setError("Veuillez sélectionner un fichier."); return; }
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await uploadCachet(file, nom || undefined);
      setSuccess("Cachet enregistré avec succès.");
      setFile(null);
      setPreview(null);
      if (fileRef.current) fileRef.current.value = "";
      await loadCachet();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Erreur lors de l'upload.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Supprimer le cachet numérique ?")) return;
    try {
      await deleteCachet();
      setCachet(null);
      setSuccess("Cachet supprimé.");
    } catch {
      setError("Erreur lors de la suppression.");
    }
  };

  if (loading) return <p className="text-gray-500 text-sm">Chargement...</p>;

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h2 className="text-sm font-medium text-gray-700 mb-1">Cachet numérique</h2>
        <p className="text-xs text-gray-400">
          Le cachet apparaîtra sur vos factures et devis. Formats acceptés : PNG, JPEG, SVG. Max 2 MB.
        </p>
      </div>

      {error   && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded text-sm">{success}</div>}

      {/* Cachet actuel */}
      {cachet && !preview && (
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 space-y-3">
          <p className="text-xs text-gray-500 font-medium">Cachet actuel</p>
          <div className="flex items-center gap-4">
            <img
              src={`${getCachetImageUrl()}?t=${Date.now()}`}
              alt="Cachet numérique"
              className="h-24 w-auto object-contain border border-gray-200 rounded bg-white p-2"
            />
            <div className="space-y-1">
              {cachet.nom && <p className="text-sm font-medium text-gray-700">{cachet.nom}</p>}
              <p className="text-xs text-gray-400">Type : {cachet.image_mime}</p>
              <p className="text-xs text-gray-400">
                Mis à jour le {new Date(cachet.updated_at).toLocaleDateString("fr-FR")}
              </p>
            </div>
          </div>
          <button onClick={handleDelete} className="text-xs text-red-500 hover:underline">
            Supprimer le cachet
          </button>
        </div>
      )}

      {/* Zone d'upload */}
      <div className="space-y-4">
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition"
          onClick={() => fileRef.current?.click()}
        >
          {preview ? (
            <img src={preview} alt="Aperçu" className="h-24 mx-auto object-contain" />
          ) : (
            <div className="space-y-1">
              <p className="text-sm text-gray-500">Cliquez pour sélectionner un fichier</p>
              <p className="text-xs text-gray-400">PNG, JPEG, SVG — max 2 MB</p>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/png,image/jpeg,image/svg+xml"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>

        {preview && (
          <div className="space-y-1">
            <Label>Nom du cachet (optionnel)</Label>
            <Input
              placeholder="ex: Cachet officiel 2025"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
            />
          </div>
        )}

        <div className="flex gap-2">
          <Button onClick={handleUpload} disabled={saving || !file}>
            {saving ? "Envoi en cours..." : cachet ? "Remplacer le cachet" : "Enregistrer le cachet"}
          </Button>
          {preview && (
            <Button variant="outline" onClick={() => { setPreview(null); setFile(null); if (fileRef.current) fileRef.current.value = ""; }}>
              Annuler
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}