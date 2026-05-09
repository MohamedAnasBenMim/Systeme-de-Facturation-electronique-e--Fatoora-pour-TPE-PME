import { useEffect, useState } from "react";
import { Settings as SettingsIcon, Building2, CreditCard, Globe, Bell, Upload, Image as ImageIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { Switch } from "../components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import api from "../../services/api";

type EntrepriseForm = {
  nom: string;
  slogan: string;
  forme_juridique: string;
  adresse: string;
  ville: string;
  code_postal: string;
  pays: string;
  telephone: string;
  email: string;
  site_web: string;
  matricule_fiscal: string;
  langue: string;
  prefixe_devis: string;
  prefixe_bc: string;
  prefixe_bl: string;
  prefixe_facture: string;
};

const initialForm: EntrepriseForm = {
  nom: "",
  slogan: "",
  forme_juridique: "",
  adresse: "",
  ville: "",
  code_postal: "",
  pays: "Tunisie",
  telephone: "",
  email: "",
  site_web: "",
  matricule_fiscal: "",
  langue: "fr",
  prefixe_devis: "DEV",
  prefixe_bc: "BC",
  prefixe_bl: "BL",
  prefixe_facture: "FAC",
};

export function SettingsPage() {
  const [form, setForm] = useState<EntrepriseForm>(initialForm);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await api.get("/entreprises/mon-profil/complet");
        const e = res.data;

        setForm({
          nom: e.nom ?? "",
          slogan: e.slogan ?? "",
          forme_juridique: e.forme_juridique ?? "",
          adresse: e.adresse ?? "",
          ville: e.ville ?? "",
          code_postal: e.code_postal ?? "",
          pays: e.pays ?? "Tunisie",
          telephone: e.telephone ?? "",
          email: e.email ?? "",
          site_web: e.site_web ?? "",
          matricule_fiscal: e.matricule_fiscal ?? "",
          langue: e.langue ?? "fr",
          pied_de_page: e.pied_de_page ?? "",
          mentions_legales: e.mentions_legales ?? "",
          prefixe_devis: e.prefixe_devis ?? "DEV",
          prefixe_bc: e.prefixe_bc ?? "BC",
          prefixe_bl: e.prefixe_bl ?? "BL",
          prefixe_facture: e.prefixe_facture ?? "FAC",
        });

        setLogoPreview(e.logo_url ?? "");
      } catch (error) {
        setMessage("Erreur lors du chargement du profil entreprise.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const setField = (key: keyof EntrepriseForm, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    if (!file) return;
    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");

    try {
      await api.put("/entreprises/mon-profil", {
        nom: form.nom,
        slogan: form.slogan || null,
        forme_juridique: form.forme_juridique || null,
        adresse: form.adresse,
        ville: form.ville,
        code_postal: form.code_postal || null,
        pays: form.pays || "Tunisie",
        telephone: form.telephone || null,
        email: form.email || null,
        site_web: form.site_web || null,
        matricule_fiscal: form.matricule_fiscal || null,
        langue: form.langue,
        prefixe_devis: form.prefixe_devis,
        prefixe_bc: form.prefixe_bc,
        prefixe_bl: form.prefixe_bl,
        prefixe_facture: form.prefixe_facture,
      });

      if (logoFile) {
        const fd = new FormData();
        fd.append("file", logoFile);
        await api.post("/entreprises/mon-profil/logo", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      setMessage("Paramètres enregistrés avec succès.");
    } catch (error) {
      setMessage("Erreur lors de l'enregistrement.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramétrage du compte</h1>
        <p className="text-gray-500 mt-1">Gérez votre profil entreprise et la configuration de l’application</p>
      </div>

      {message && (
        <div className="rounded-lg bg-blue-50 text-blue-700 px-4 py-3 text-sm border border-blue-100">
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Profil entreprise
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-xl border border-dashed border-gray-300 flex items-center justify-center overflow-hidden bg-gray-50">
                {logoPreview ? (
                  <img src={logoPreview} alt="Logo" className="w-full h-full object-cover" />
                ) : (
                  <ImageIcon className="w-8 h-8 text-gray-400" />
                )}
              </div>
              <div className="flex-1 space-y-2">
                <Label htmlFor="logo">Logo de l’entreprise</Label>
                <Input id="logo" type="file" accept="image/*" onChange={handleLogoChange} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="nom">Nom de l'entreprise</Label>
              <Input id="nom" value={form.nom} onChange={(e) => setField("nom", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="slogan">Slogan</Label>
              <Input id="slogan" value={form.slogan} onChange={(e) => setField("slogan", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="forme_juridique">Forme juridique</Label>
              <Input id="forme_juridique" value={form.forme_juridique} onChange={(e) => setField("forme_juridique", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="matricule_fiscal">Matricule fiscal</Label>
              <Input id="matricule_fiscal" value={form.matricule_fiscal} onChange={(e) => setField("matricule_fiscal", e.target.value)} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Coordonnées
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="adresse">Adresse</Label>
              <Input id="adresse" value={form.adresse} onChange={(e) => setField("adresse", e.target.value)} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ville">Ville</Label>
                <Input id="ville" value={form.ville} onChange={(e) => setField("ville", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="code_postal">Code postal</Label>
                <Input id="code_postal" value={form.code_postal} onChange={(e) => setField("code_postal", e.target.value)} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="pays">Pays</Label>
              <Input id="pays" value={form.pays} onChange={(e) => setField("pays", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="telephone">Téléphone</Label>
              <Input id="telephone" value={form.telephone} onChange={(e) => setField("telephone", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input id="email" type="email" value={form.email} onChange={(e) => setField("email", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="site_web">Site web</Label>
              <Input id="site_web" value={form.site_web} onChange={(e) => setField("site_web", e.target.value)} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Langue et documents
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="langue">Langue</Label>
              <Select value={form.langue} onValueChange={(v) => setField("langue", v)}>
                <SelectTrigger id="langue">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="ar">Arabe</SelectItem>
                </SelectContent>
              </Select>
            </div>

            

            
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SettingsIcon className="w-5 h-5" />
              Numérotation des documents
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prefixe_devis">Préfixe devis</Label>
              <Input id="prefixe_devis" value={form.prefixe_devis} onChange={(e) => setField("prefixe_devis", e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="prefixe_bc">Préfixe bons de commande</Label>
              <Input id="prefixe_bc" value={form.prefixe_bc} onChange={(e) => setField("prefixe_bc", e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="prefixe_bl">Préfixe bons de livraison</Label>
              <Input id="prefixe_bl" value={form.prefixe_bl} onChange={(e) => setField("prefixe_bl", e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="prefixe_facture">Préfixe facture</Label>
              <Input id="prefixe_facture" value={form.prefixe_facture} onChange={(e) => setField("prefixe_facture", e.target.value)} />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={loading || saving}>
          {saving ? "Enregistrement..." : "Enregistrer les modifications"}
        </Button>
      </div>
    </div>
  );
}