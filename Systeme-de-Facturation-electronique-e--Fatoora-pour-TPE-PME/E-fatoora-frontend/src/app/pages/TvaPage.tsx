// src/pages/ParametresPage.tsx
import { useState } from "react";
import { TaxesSection }  from "../components/parametres/TaxeSection";
import { CachetSection } from "../components/parametres/CachetSection";

type Tab = "taxes" | "cachet";

export default function ParametresPage() {
  const [tab, setTab] = useState<Tab>("taxes");

  const tabs: { key: Tab; label: string }[] = [
    { key: "taxes",  label: "Gestion des taxes"   },
    { key: "cachet", label: "Cachet numérique"     },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Paramètres</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.key
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "taxes"  && <TaxesSection />}
      {tab === "cachet" && <CachetSection />}
    </div>
  );
}