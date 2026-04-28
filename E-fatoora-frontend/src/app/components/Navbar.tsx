import { useEffect, useState } from "react";
import { Search, Bell, User } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import api from "../../services/api";

type UtilisateurConnecte = {
  nom?: string;
  prenom?: string;
  email?: string;
};

export function Navbar() {
  const [utilisateur, setUtilisateur] = useState<UtilisateurConnecte | null>(null);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    const chargerUtilisateur = async () => {
      try {
        // ✅ axios à la place de fetch — token ajouté automatiquement
        const response = await api.get("/users/me");
        setUtilisateur(response.data);
      } catch (error) {
        console.error("Impossible de charger l'utilisateur connecté", error);
        setUtilisateur(null);
      } finally {
        setChargement(false);
      }
    };

    chargerUtilisateur();
  }, []);

  const nomAffiche = utilisateur
    ? `${utilisateur.prenom ?? ""} ${utilisateur.nom ?? ""}`.trim() || utilisateur.email || "Utilisateur"
    : "Utilisateur";

  const emailAffiche = utilisateur?.email ?? "";

  return (
    <header className="bg-white border-b border-gray-200 px-8 py-4">
      <div className="flex items-center justify-between">
        <div className="flex-1 max-w-lg">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search invoices, clients..."
              className="pl-10 bg-gray-50 border-gray-200"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button>

          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {chargement ? "Chargement..." : nomAffiche}
              </p>
              <p className="text-xs text-gray-500">
                {chargement ? "" : emailAffiche}
              </p>
            </div>
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}