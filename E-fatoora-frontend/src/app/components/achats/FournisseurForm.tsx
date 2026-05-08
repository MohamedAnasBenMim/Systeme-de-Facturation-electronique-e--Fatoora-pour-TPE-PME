import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent } from "../ui/card";
import type { Fournisseur } from "../../../services/achatsService";

interface Props {
  initial?: Fournisseur;
  onCancel: () => void;
  onSubmit: (data: Partial<Fournisseur>) => Promise<void>;
}


interface FieldProps {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}

function Field({ label, required, children }: FieldProps) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {children}
    </div>
  );
}

const inputCls =
  "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900";

export function FournisseurForm({ initial, onCancel, onSubmit }: Props) {
  const [loading, setLoading] = useState(false);

  //  Un useState par champ — évite la recréation de l'objet form entier
  const [nom, setNom]                                 = useState(initial?.nom ?? "");
  const [matricule_fiscal, setMatriculeFiscal]         = useState(initial?.matricule_fiscal ?? "");
  const [adresse, setAdresse]                         = useState(initial?.adresse ?? "");
  const [ville, setVille]                             = useState(initial?.ville ?? "");
  const [code_postal, setCodePostal]                   = useState(initial?.code_postal ?? "");
  const [telephone, setTelephone]                     = useState(initial?.telephone ?? "");
  const [email, setEmail]                             = useState(initial?.email ?? "");
  const [contact_principal, setContactPrincipal]       = useState(initial?.contact_principal ?? "");
  const [delai_paiement_jours, setDelaiPaiementJours] = useState(initial?.delai_paiement_jours ?? 30);
  const [escompte_pourcent, setEscomptePourcent]       = useState(initial?.escompte_pourcent ?? 0);
  const [seuil_tolerance_quantite, setSeuilQte]       = useState(initial?.seuil_tolerance_quantite ?? 5);
  const [seuil_tolerance_prix, setSeuilPrix]           = useState(initial?.seuil_tolerance_prix ?? 5);
  const [actif, setActif]                             = useState(initial?.actif ?? true);

  const handleSubmit = async () => {
    if (!nom.trim())              return alert("Le nom est obligatoire.");
    if (!matricule_fiscal.trim()) return alert("La matricule fiscale est obligatoire.");
    if (!adresse.trim())          return alert("L'adresse est obligatoire.");
    if (!ville.trim())            return alert("La ville est obligatoire.");

    setLoading(true);
    try {
      await onSubmit({
        nom,
        matricule_fiscal,
        adresse,
        ville,
        code_postal,
        telephone,
        email,
        contact_principal,
        delai_paiement_jours,
        escompte_pourcent,
        seuil_tolerance_quantite,
        seuil_tolerance_prix,
        actif,
      });
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erreur lors de l'enregistrement");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center gap-4">
        <button onClick={onCancel} className="p-2 hover:bg-slate-100 rounded-lg transition">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {initial ? "Modifier le fournisseur" : "Nouveau fournisseur"}
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Renseignez les informations du fournisseur
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Colonne principale */}
        <Card className="col-span-2 border border-slate-200 shadow-sm">
          <CardContent className="p-6 space-y-6">

            {/* Identification */}
            <div>
              <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                Identification
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Nom du fournisseur" required>
                  <input
                    value={nom}
                    onChange={e => setNom(e.target.value)}
                    className={inputCls}
                    placeholder="Société XYZ"
                  />
                </Field>

                <Field label="Matricule fiscale" required>
                  <input
                    value={matricule_fiscal}
                    onChange={e => setMatriculeFiscal(e.target.value)}
                    className={inputCls}
                    placeholder="1234567/A/M/000"
                  />
                </Field>

                <Field label="Adresse" required>
                  <input
                    value={adresse}
                    onChange={e => setAdresse(e.target.value)}
                    className={inputCls}
                    placeholder="Rue et numéro"
                  />
                </Field>

                <div className="grid grid-cols-2 gap-2">
                  <Field label="Ville" required>
                    <input
                      value={ville}
                      onChange={e => setVille(e.target.value)}
                      className={inputCls}
                      placeholder="Tunis"
                    />
                  </Field>
                  <Field label="Code postal">
                    <input
                      value={code_postal}
                      onChange={e => setCodePostal(e.target.value)}
                      className={inputCls}
                      placeholder="1000"
                    />
                  </Field>
                </div>
              </div>
            </div>

            {/* Contact */}
            <div>
              <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                Contact
              </h2>
              <div className="grid grid-cols-3 gap-4">
                <Field label="Contact principal">
                  <input
                    value={contact_principal}
                    onChange={e => setContactPrincipal(e.target.value)}
                    className={inputCls}
                    placeholder="Nom Prénom"
                  />
                </Field>

                <Field label="Email">
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className={inputCls}
                    placeholder="contact@fournisseur.tn"
                  />
                </Field>

                <Field label="Téléphone">
                  <input
                    value={telephone}
                    onChange={e => setTelephone(e.target.value)}
                    className={inputCls}
                    placeholder="+216 XX XXX XXX"
                  />
                </Field>
              </div>
            </div>

            {/* Seuils rapprochement */}
            <div>
              <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                Paramètres de rapprochement (3-way match)
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Seuil tolérance quantité (%)">
                  <input
                    type="number"
                    min={0}
                    max={100}
                    step={0.1}
                    value={seuil_tolerance_quantite}
                    onChange={e => setSeuilQte(parseFloat(e.target.value) || 0)}
                    className={inputCls}
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    Écart de quantité toléré entre BC et facture
                  </p>
                </Field>

                <Field label="Seuil tolérance prix (%)">
                  <input
                    type="number"
                    min={0}
                    max={100}
                    step={0.1}
                    value={seuil_tolerance_prix}
                    onChange={e => setSeuilPrix(parseFloat(e.target.value) || 0)}
                    className={inputCls}
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    Écart de prix toléré avant blocage en litige
                  </p>
                </Field>
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Colonne droite */}
        <div className="space-y-4">
          <Card className="border border-slate-200 shadow-sm">
            <CardContent className="p-6 space-y-4">
              <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Conditions commerciales
              </h2>

              <Field label="Délai de paiement (jours)">
                <select
                  value={delai_paiement_jours}
                  onChange={e => setDelaiPaiementJours(parseInt(e.target.value))}
                  className={inputCls}
                >
                  <option value={0}>Immédiat</option>
                  <option value={30}>30 jours</option>
                  <option value={60}>60 jours</option>
                  <option value={90}>90 jours</option>
                </select>
              </Field>

              <Field label="Escompte si paiement anticipé (%)">
                <input
                  type="number"
                  min={0}
                  max={100}
                  step={0.1}
                  value={escompte_pourcent}
                  onChange={e => setEscomptePourcent(parseFloat(e.target.value) || 0)}
                  className={inputCls}
                />
              </Field>

              <Field label="Statut">
                <select
                  value={actif ? "true" : "false"}
                  onChange={e => setActif(e.target.value === "true")}
                  className={inputCls}
                >
                  <option value="true">Actif</option>
                  <option value="false">Inactif</option>
                </select>
              </Field>
            </CardContent>
          </Card>

          <div className="flex flex-col gap-3">
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-slate-900 hover:bg-slate-700 w-full"
            >
              {loading
                ? "Enregistrement..."
                : initial
                ? "Enregistrer les modifications"
                : "Créer le fournisseur"}
            </Button>
            <Button variant="outline" onClick={onCancel} className="w-full">
              Annuler
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}