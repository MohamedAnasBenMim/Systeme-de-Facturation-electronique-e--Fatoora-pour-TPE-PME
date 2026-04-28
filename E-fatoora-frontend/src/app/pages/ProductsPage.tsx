import { 
  FileEdit, Plus, Download, Upload, TrendingUp, Search, 
  Package, Wrench, MoreHorizontal, Trash2, AlertCircle, CheckCircle2 
} from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useState, useEffect, useRef } from "react";
import {
  getProduits, deleteProduit, bulkUpdatePrix,
  importCSV, exportCSV, getCategories, getUnites,
  Produit, Categorie, UniteMesure, SearchParams, TypeArticle,
} from "../../services/productService";
import { ProduitModal } from "../components/catalogue/ProduitModal";

export default function ProductsPage() {
  const [produits, setProduits] = useState<Produit[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [categories, setCategories] = useState<Categorie[]>([]);
  const [unites, setUnites] = useState<UniteMesure[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<TypeArticle | "">("");
  const [catFilter, setCatFilter] = useState<number | "">("");
  const [showModal, setShowModal] = useState(false);
  const [editProduit, setEditProduit] = useState<Produit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [showBulk, setShowBulk] = useState(false);
  const [bulkPct, setBulkPct] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { 
    const delayDebounceFn = setTimeout(() => { loadProduits(); }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [page, search, typeFilter, catFilter]);

  const loadAll = async () => {
    try {
      const [c, u] = await Promise.all([getCategories(), getUnites()]);
      setCategories(c.data);
      setUnites(u.data);
    } catch (err) { console.error(err); }
  };

  const loadProduits = async () => {
    setLoading(true);
    try {
      const params: SearchParams = { page, limit: 12 };
      if (search) params.q = search;
      if (typeFilter) params.type = typeFilter;
      if (catFilter) params.categorie_id = catFilter as number;
      const { data } = await getProduits(params);
      setProduits(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch { setError("Erreur de chargement"); }
    finally { setLoading(false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Voulez-vous vraiment désactiver ce produit ?")) return;
    await deleteProduit(id);
    setSuccess("Le produit a été désactivé avec succès.");
    setTimeout(() => setSuccess(null), 3000);
    loadProduits();
  };

  return (
    <div className="p-8 bg-gray-50/50 min-h-screen space-y-8 max-w-[1600px] mx-auto">
      
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Catalogue Articles</h1>
          <p className="text-gray-500 mt-1 flex items-center gap-2">
            <Package className="w-4 h-4" />
            {total} références enregistrées
          </p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          <div className="flex bg-white border border-gray-200 rounded-lg p-1 shadow-sm">
            <Button variant="ghost" size="sm" onClick={() => setShowBulk(true)} className="text-gray-600 hover:text-blue-600">
              <TrendingUp className="w-4 h-4 mr-2" />
              Prix
            </Button>
            <div className="w-[1px] bg-gray-200 my-1 mx-1" />
            <Button variant="ghost" size="sm" onClick={() => fileRef.current?.click()} disabled={importing} className="text-gray-600">
              <Upload className="w-4 h-4 mr-2" />
              Import
            </Button>
            <Button variant="ghost" size="sm" onClick={loadProduits} className="text-gray-600">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
          
          <Button onClick={() => { setEditProduit(null); setShowModal(true); }} className="bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-100">
            <Plus className="w-4 h-4 mr-2 font-bold" />
            Nouveau Produit
          </Button>
          <input ref={fileRef} type="file" accept=".csv" className="hidden" />
        </div>
      </div>

      
      {success && (
        <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-200 text-emerald-800 px-5 py-3 rounded-xl shadow-sm animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          <span className="text-sm font-medium">{success}</span>
        </div>
      )}

      
      <Card className="border-none shadow-sm bg-white">
        <CardContent className="p-4 flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[300px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Rechercher par nom, référence ou SKU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 bg-gray-50 border-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-all"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as TypeArticle | "")}
              className="bg-gray-50 border-none rounded-lg px-4 py-2 text-sm font-medium text-gray-600 focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              <option value="">Tous les types</option>
              <option value="PRODUIT">📦 Produits</option>
              <option value="SERVICE">🛠️ Services</option>
            </select>
            <select
              value={catFilter}
              onChange={(e) => setCatFilter(e.target.value ? parseInt(e.target.value) : "")}
              className="bg-gray-50 border-none rounded-lg px-4 py-2 text-sm font-medium text-gray-600 focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              <option value="">Toutes catégories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.nom}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* ── Liste des Produits ── */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
           {[...Array(6)].map((_, i) => <div key={i} className="h-48 bg-gray-200 rounded-2xl" />)}
        </div>
      ) : produits.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-100">
           <Package className="w-16 h-16 text-gray-200 mx-auto mb-4" />
           <p className="text-gray-500 font-medium">Aucun article ne correspond à votre recherche</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {produits.map((p) => (
            <Card key={p.id} className="group overflow-hidden border-none shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 bg-white">
              <div className="relative h-40 bg-gray-100 flex items-center justify-center overflow-hidden">
                {p.image_url ? (
                  <img src={p.image_url} alt={p.designation} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                ) : (
                  <div className="text-gray-300">
                    {p.type === "SERVICE" ? <Wrench size={48} /> : <Package size={48} />}
                  </div>
                )}
                <div className="absolute top-3 left-3">
                  <span className={`text-[10px] uppercase tracking-widest font-bold px-2 py-1 rounded-md shadow-sm ${
                    p.type === "SERVICE" ? "bg-purple-600 text-white" : "bg-blue-600 text-white"
                  }`}>
                    {p.type}
                  </span>
                </div>
              </div>
              
              <CardContent className="p-5">
                <div className="mb-4">
                  <p className="text-xs text-blue-600 font-bold uppercase tracking-tighter mb-1">{p.categorie?.nom || "Sans catégorie"}</p>
                  <h3 className="font-bold text-gray-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                    {p.designation}
                  </h3>
                  <p className="text-xs font-mono text-gray-400 mt-1">{p.reference || "REF-PAS-DE-REF"}</p>
                </div>

                <div className="flex items-end justify-between border-t border-gray-50 pt-4">
                  <div>
                    <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Prix Vente TTC</p>
                    <p className="text-xl font-black text-gray-900">
                      {p.prix_vente_ttc?.toLocaleString('fr-TN', { minimumFractionDigits: 3 })} <span className="text-xs font-normal text-gray-400">TND</span>
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="secondary" size="icon" onClick={() => { setEditProduit(p); setShowModal(true); }} className="h-8 w-8 rounded-full bg-gray-50 hover:bg-blue-50 hover:text-blue-600">
                      <FileEdit className="w-4 h-4" />
                    </Button>
                    <Button variant="secondary" size="icon" onClick={() => handleDelete(p.id)} className="h-8 w-8 rounded-full bg-gray-50 hover:bg-red-50 hover:text-red-600 text-gray-400">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* ── Pagination Purifiée ── */}
      {pages > 1 && (
        <div className="flex justify-center items-center gap-3 pt-8">
          <Button 
            variant="outline" 
            disabled={page === 1} 
            onClick={() => setPage(page - 1)}
            className="rounded-xl"
          >Précédent</Button>
          <div className="flex gap-2">
            {[...Array(pages)].map((_, i) => (
              <button
                key={i}
                onClick={() => setPage(i + 1)}
                className={`w-10 h-10 rounded-xl font-bold transition-all ${
                  page === i + 1 ? "bg-blue-600 text-white shadow-lg shadow-blue-200" : "bg-white text-gray-400 hover:bg-gray-100"
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
          <Button 
            variant="outline" 
            disabled={page === pages} 
            onClick={() => setPage(page + 1)}
            className="rounded-xl"
          >Suivant</Button>
        </div>
      )}

      
      {showBulk && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md border-none shadow-2xl animate-in zoom-in-95 duration-200">
            <CardContent className="p-8 space-y-6">
              <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600">
                <TrendingUp size={24} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Mise à jour des tarifs</h2>
                <p className="text-sm text-gray-500 mt-1">Appliquez une variation en % sur l'ensemble de votre catalogue.</p>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest">Pourcentage (%)</label>
                <Input
                  type="number"
                  placeholder="Ex: 5 ou -3"
                  value={bulkPct}
                  onChange={(e) => setBulkPct(parseFloat(e.target.value))}
                  className="h-12 text-lg font-bold"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button onClick={() => setShowBulk(false)} variant="ghost" className="flex-1 h-12 text-gray-500">Annuler</Button>
                <Button onClick={handleBulk} className="flex-1 h-12 bg-blue-600 hover:bg-blue-700">Confirmer</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showModal && (
        <ProduitModal
          produit={editProduit}
          categories={categories}
          unites={unites}
          onClose={() => { setShowModal(false); setEditProduit(null); }}
          onSaved={() => { setShowModal(false); setEditProduit(null); loadProduits(); }}
        />
      )}
    </div>
  );
}