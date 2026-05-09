import React, { useEffect, useMemo, useState } from "react";
import api from "../../services/api";
import { Plus, X, Landmark, CreditCard, Building2, Calendar, Pencil, Trash2, RefreshCw } from "lucide-react";

interface BankAccount {
  id: number;
  banque: string;
  agence?: string | null;
  rib: string;
  iban?: string | null;
  swift?: string | null;
  devise?: string;
  date_creation?: string;
}

interface BankAccountForm {
  banque: string;
  agence: string;
  rib: string;
  iban: string;
  swift: string;
  devise: string;
}

const emptyForm: BankAccountForm = {
  banque: "",
  agence: "",
  rib: "",
  iban: "",
  swift: "",
  devise: "TND",
};

const BankAccountsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<BankAccountForm>(emptyForm);
  const [error, setError] = useState<string | null>(null);

  const isEditing = useMemo(() => editingId !== null, [editingId]);

  const loadAccounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/comptes-bancaires/");
      const data = Array.isArray(res.data) ? res.data : res.data?.items ?? res.data?.data ?? [];
      setAccounts(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Erreur lors du chargement des comptes bancaires.");
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const openCreateModal = () => {
    setEditingId(null);
    setForm(emptyForm);
    setIsModalOpen(true);
  };

  const openEditModal = (acc: BankAccount) => {
    setEditingId(acc.id);
    setForm({
      banque: acc.banque || "",
      agence: acc.agence || "",
      rib: acc.rib || "",
      iban: acc.iban || "",
      swift: acc.swift || "",
      devise: acc.devise || "TND",
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    setForm(emptyForm);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const payload = {
        banque: form.banque,
        agence: form.agence || null,
        rib: form.rib,
        iban: form.iban || null,
        swift: form.swift || null,
        devise: form.devise,
      };

      if (isEditing && editingId !== null) {
        await api.put(`/comptes-bancaires/${editingId}`, payload);
      } else {
        await api.post("/comptes-bancaires/", payload);
      }

      closeModal();
      await loadAccounts();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Erreur lors de l'enregistrement.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Supprimer ce compte bancaire ?")) return;

    setSaving(true);
    setError(null);
    try {
      await api.delete(`/comptes-bancaires/${id}`);
      await loadAccounts();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Erreur lors de la suppression.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-8 font-sans">
      <div className="max-w-6xl mx-auto mb-10 flex items-center justify-between">
        <div className="flex flex-col gap-1">
          
        </div>

        <div className="flex gap-2">
          <button
            onClick={loadAccounts}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          >
            <RefreshCw size={16} />
            Rafraîchir
          </button>
          <button
            onClick={openCreateModal}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#1a1c2e] text-white hover:bg-[#272a42]"
          >
            <Plus size={16} />
            Nouveau compte
          </button>
        </div>
      </div>

      {error && (
        <div className="max-w-6xl mx-auto mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center text-slate-500 py-10">Chargement...</div>
        ) : accounts.length === 0 ? (
          <div className="col-span-full text-center text-slate-500 py-10">
            Aucun compte bancaire trouvé.
          </div>
        ) : (
          accounts.map((acc) => (
            <div
              key={acc.id}
              className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-8 bg-slate-50 border border-slate-100 flex items-center justify-center font-bold text-[#1a1c2e] text-xs italic rounded shadow-inner">
                    {acc.banque?.slice(0, 3).toUpperCase()}
                  </div>
                  <span className="text-slate-700 font-bold text-sm">{acc.banque}</span>
                </div>

                <div className="flex gap-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition">
                  <button
                    onClick={() => openEditModal(acc)}
                    className="p-2 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100"
                    title="Modifier"
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(acc.id)}
                    className="p-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100"
                    title="Supprimer"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-[#1a1c2e] font-bold text-lg tracking-tight leading-relaxed break-words">
                  {acc.rib}
                </p>
              </div>

              <div className="space-y-1 text-sm text-slate-500">
                {acc.agence && (
                  <p className="flex items-center gap-2">
                    <Building2 size={12} />
                    {acc.agence}
                  </p>
                )}
                {acc.iban && <p className="truncate">IBAN : {acc.iban}</p>}
                {acc.swift && <p className="truncate">SWIFT : {acc.swift}</p>}
                <p className="flex items-center gap-2">
                  <Calendar size={12} />
                  <span>
                    Date : {acc.date_creation ? new Date(acc.date_creation).toLocaleString("fr-FR") : "—"}
                  </span>
                </p>
              </div>
            </div>
          ))
        )}

        <button
          onClick={openCreateModal}
          className="bg-[#F0F9FF] border-2 border-dashed border-[#0EA5E9] rounded-xl flex items-center justify-center min-h-[180px] hover:bg-[#E0F2FE] transition-colors group"
        >
          <div className="w-14 h-14 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
            <Plus size={48} className="text-[#0EA5E9]" strokeWidth={1.5} />
          </div>
        </button>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-[#1a1c2e]/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl overflow-hidden">
            <div className="p-6 bg-[#1a1c2e] text-white flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/20 rounded-xl">
                  <Landmark className="text-purple-400" size={24} />
                </div>
                <div>
                  <h3 className="font-black uppercase text-sm tracking-widest">
                    {isEditing ? "Modifier un compte" : "Enregistrer un compte"}
                  </h3>
                  <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                    Paramètres du compte bancaire
                  </p>
                </div>
              </div>
              <button onClick={closeModal} className="hover:bg-white/10 p-2 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-8 space-y-6">
              <div className="space-y-1">
                <label className="text-[10px] font-black text-slate-400 uppercase ml-1 tracking-widest">
                  Banque
                </label>
                <div className="relative">
                  <Building2 className="absolute left-4 top-4 text-slate-300" size={18} />
                  <input
                    name="banque"
                    type="text"
                    value={form.banque}
                    onChange={handleChange}
                    placeholder="Ex: BIAT, BNA, Amen Bank..."
                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 pl-12 text-sm font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-slate-700"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-black text-slate-400 uppercase ml-1 tracking-widest">
                  RIB
                </label>
                <div className="relative">
                  <CreditCard className="absolute left-4 top-4 text-slate-300" size={18} />
                  <input
                    name="rib"
                    type="text"
                    value={form.rib}
                    onChange={handleChange}
                    placeholder="TN59 0000 0000 0000 0000 0000"
                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 pl-12 text-sm font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-slate-700"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-black text-slate-400 uppercase ml-1 tracking-widest">
                  Agence
                </label>
                <div className="relative">
                  <Building2 className="absolute left-4 top-4 text-slate-300" size={18} />
                  <input
                    name="agence"
                    type="text"
                    value={form.agence}
                    onChange={handleChange}
                    placeholder="Ex: Agence Lac 2, Tunis..."
                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 pl-12 text-sm font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-slate-700"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1 col-span-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase ml-1 tracking-widest">
                    IBAN
                  </label>
                  <input
                    name="iban"
                    type="text"
                    value={form.iban}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 text-sm font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-slate-700"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-black text-slate-400 uppercase ml-1 tracking-widest">
                    Devise
                  </label>
                  <select
                    name="devise"
                    value={form.devise}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 text-sm font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-slate-700"
                  >
                    <option value="TND">TND</option>
                    <option value="EUR">EUR</option>
                    <option value="USD">USD</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-black text-slate-400 uppercase ml-1 tracking-widest">
                  SWIFT
                </label>
                <input
                  name="swift"
                  type="text"
                  value={form.swift}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 text-sm font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-slate-700"
                />
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 py-4 text-slate-500 font-bold uppercase text-[11px] tracking-widest hover:bg-slate-50 rounded-2xl transition-all"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-4 bg-[#a855f7] text-white font-black uppercase text-[11px] tracking-widest rounded-2xl shadow-lg shadow-purple-200 hover:bg-purple-600 transition-all disabled:opacity-60"
                >
                  {saving ? "Enregistrement..." : isEditing ? "Modifier" : "Enregistrer"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BankAccountsPage;