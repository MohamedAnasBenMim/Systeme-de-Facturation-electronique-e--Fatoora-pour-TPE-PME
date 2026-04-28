import { Link, useLocation } from "react-router";
import { useState } from "react";
import {
  LayoutDashboard,
  Users,
  FileText,
  FileEdit,
  Wallet,
  Package,
  BarChart3,
  Settings,
  ChevronDown,
  Building2,
  UserRound,
  Landmark,
  FolderOpen,
  Languages,
} from "lucide-react";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: Users, label: "Clients", path: "/clients" },
  { icon: Wallet, label: "Expenses / Dépenses", path: "/expenses" },
  { icon: Package, label: "Produits & Services", path: "/products" },
  { icon: BarChart3, label: "Reports / Rapports", path: "/reports" },
];

const ventesItems = [
  { icon: FileText, label: "Factures", path: "/invoices" },
  { icon: FileEdit, label: "Devis", path: "/quotes" },
];

const AchatsItems = [
  { icon: FileText, label: "Factures", path: "/invoices" },
  { icon: FileEdit, label: "Devis", path: "/quotes" },
];

const profileEntrepriseItems = [
  { icon: UserRound, label: "Membres", path: "/profile-entreprise/membres" },
  { icon: Landmark, label: "Comptes bancaires", path: "/compte" },
  { icon: Settings, label: "Paramètres", path: "/settings" },
  { icon: FolderOpen, label: "Documents", path: "/profile-entreprise/documents" },
  { icon: Languages, label: "Langue", path: "/profile-entreprise/langue" },
];

export function Sidebar() {
  const location = useLocation();
  const [profileOpen, setProfileOpen] = useState(false);
  const [ventesOpen, setVentesOpen] = useState(false);
  const [achatsOpen, setAchatsOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;
  const isProfileSection = location.pathname.startsWith("/profile-entreprise");
  const isVentesSection = location.pathname.startsWith("/invoices") || location.pathname.startsWith("/quotes");
  const isAchatsSection = location.pathname.startsWith("/achats");

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 p-6 overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-blue-600">E-Fatoora</h1>
        <p className="text-sm text-gray-500">Invoicing Platform</p>
      </div>

      <nav className="space-y-2">
        {/* Main menu */}
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                active ? "bg-blue-50 text-blue-600" : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm">{item.label}</span>
            </Link>
          );
        })}

        {/* Section Vente */}
        <div className="pt-2">
          <button
            type="button"
            onClick={() => setVentesOpen((prev) => !prev)}
            className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-lg transition-colors ${
              isVentesSection ? "bg-blue-50 text-blue-600" : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5" />
              <span className="text-sm font-medium">Vente</span>
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform ${ventesOpen || isVentesSection ? "rotate-180" : ""}`}
            />
          </button>

          {(ventesOpen || isVentesSection) && (
            <div className="mt-2 ml-4 space-y-1 border-l border-gray-200 pl-3">
              {ventesItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                      active ? "bg-blue-50 text-blue-600" : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        {/* Section Achats */}
        <div className="pt-2">
          <button
            type="button"
            onClick={() => setAchatsOpen((prev) => !prev)}
            className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-lg transition-colors ${
              isAchatsSection ? "bg-blue-50 text-blue-600" : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5" />
              <span className="text-sm font-medium">Achats</span>
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform ${achatsOpen || isAchatsSection ? "rotate-180" : ""}`}
            />
          </button>

          {(achatsOpen || isAchatsSection) && (
            <div className="mt-2 ml-4 space-y-1 border-l border-gray-200 pl-3">
              {AchatsItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                      active ? "bg-blue-50 text-blue-600" : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          )}
        </div>


        {/* Section Profile entreprise */}
        <div className="pt-2">
          <button
            type="button"
            onClick={() => setProfileOpen((prev) => !prev)}
            className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-lg transition-colors ${
              isProfileSection ? "bg-blue-50 text-blue-600" : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <div className="flex items-center gap-3">
              <Building2 className="w-5 h-5" />
              <span className="text-sm font-medium">Profile entreprise</span>
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform ${profileOpen || isProfileSection ? "rotate-180" : ""}`}
            />
          </button>

          {(profileOpen || isProfileSection) && (
            <div className="mt-2 ml-4 space-y-1 border-l border-gray-200 pl-3">
              {profileEntrepriseItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                      active ? "bg-blue-50 text-blue-600" : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </nav>
    </aside>
  );
}