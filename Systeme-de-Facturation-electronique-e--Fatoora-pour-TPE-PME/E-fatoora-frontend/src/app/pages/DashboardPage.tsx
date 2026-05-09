import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { TrendingUp, TrendingDown, DollarSign, FileText, Plus, Loader2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "../components/ui/table";
import {
  LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import api from "../../services/api";

// ─── Types ────────────────────────────────────────────────────────────────────

interface DashboardStats {
  revenus: number;
  chiffre_affaires: number;
  creances_en_attente: number;
  nombre_factures: number;
  depenses: number;
  depenses_en_attente: number;
  repartition_depenses: Record<string, number>;
  profit: number;
}

interface ClientFidele {
  client_id: number;
  nb_factures: number;
  ca_total: number;
}

// ─── Config ───────────────────────────────────────────────────────────────────


const PIE_COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#ef4444"];

// ─── Helpers ──────────────────────────────────────────────────────────────────

// Utilise l'instance axios — baseURL "/api/v1" + token JWT ajouté automatiquement
async function apiFetch<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  const res = await api.get<T>(path, { params });
  return res.data;
}

function formatTND(value: number) {
  return `${value.toLocaleString("fr-TN", { maximumFractionDigits: 3 })} TND`;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function KpiCard({
  title, value, sub, trend, icon: Icon, color, bgColor,
}: {
  title: string; value: string; sub: string;
  trend: "up" | "down" | "neutral";
  icon: React.ElementType; color: string; bgColor: string;
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-500 mb-1">{title}</p>
            <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
            <p className={`text-sm mt-2 ${
              trend === "up" ? "text-green-600" :
              trend === "down" ? "text-red-600" : "text-orange-600"
            }`}>
              {sub}
            </p>
          </div>
          <div className={`${bgColor} p-3 rounded-lg`}>
            <Icon className={`w-6 h-6 ${color}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm">
      <AlertCircle className="w-4 h-4 shrink-0" />
      {message}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [clients, setClients] = useState<ClientFidele[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [statsData, clientsData] = await Promise.all([
          apiFetch<DashboardStats>("/dashboard/stats", {
          }),
          apiFetch<ClientFidele[]>("/dashboard/clients-fideles", {
            limite: 5,
          }),
        ]);
        setStats(statsData);
        setClients(clientsData);
      } catch (e) {
        setError("Impossible de charger les données. Vérifiez la connexion à l'API Gateway.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // ── KPI cards dérivés des stats réelles ──
  const kpiCards = stats
    ? [
        {
          title: "Revenue / Revenu",
          value: formatTND(stats.revenus),
          sub: `CA total : ${formatTND(stats.chiffre_affaires)}`,
          trend: "up" as const,
          icon: DollarSign,
          color: "text-green-600",
          bgColor: "bg-green-50",
        },
        {
          title: "Expenses / Dépenses",
          value: formatTND(stats.depenses),
          sub: `En attente : ${formatTND(stats.depenses_en_attente)}`,
          trend: "down" as const,
          icon: TrendingDown,
          color: "text-red-600",
          bgColor: "bg-red-50",
        },
        {
          title: "Profit / Bénéfice",
          value: formatTND(stats.profit),
          sub: stats.profit >= 0 ? "Positif ✓" : "Déficitaire ✗",
          trend: stats.profit >= 0 ? ("up" as const) : ("down" as const),
          icon: TrendingUp,
          color: "text-blue-600",
          bgColor: "bg-blue-50",
        },
        {
          title: "Créances / En attente",
          value: formatTND(stats.creances_en_attente),
          sub: `${stats.nombre_factures} factures émises`,
          trend: "neutral" as const,
          icon: FileText,
          color: "text-orange-600",
          bgColor: "bg-orange-50",
        },
      ]
    : [];

  // ── Pie data depuis repartition_par_categorie ──
  const pieData = stats
    ? Object.entries(stats.repartition_depenses).map(([name, value], i) => ({
        name,
        value,
        color: PIE_COLORS[i % PIE_COLORS.length],
      }))
    : [];

  // ── Bar data depuis clients fidèles ──
  const clientsChartData = clients.map((c) => ({
    name: `Client #${c.client_id}`,
    ca: c.ca_total,
    factures: c.nb_factures,
  }));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Bienvenue, Ahmed !</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => navigate("/clients")}>
            <Plus className="w-4 h-4 mr-2" />
            Ajouter client
          </Button>
          <Button onClick={() => navigate("/invoices?new=1")}>
            <Plus className="w-4 h-4 mr-2" />
            Créer facture
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && <ErrorBanner message={error} />}

      {/* Loading overlay */}
      {loading ? (
        <div className="flex items-center justify-center py-24 text-gray-400">
          <Loader2 className="w-8 h-8 animate-spin mr-3" />
          Chargement des données…
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpiCards.map((kpi) => (
              <KpiCard key={kpi.title} {...kpi} />
            ))}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top clients bar chart */}
            <Card>
              <CardHeader>
                <CardTitle>Top Clients / Clients fidèles</CardTitle>
              </CardHeader>
              <CardContent>
                {clientsChartData.length === 0 ? (
                  <p className="text-sm text-gray-400 py-10 text-center">Aucune donnée client</p>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={clientsChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 11 }} />
                      <YAxis stroke="#6b7280" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#fff",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                        }}
                        formatter={(v: number) => formatTND(v)}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="ca"
                        name="CA Total (TND)"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={{ fill: "#3b82f6", r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* Expense pie */}
            <Card>
              <CardHeader>
                <CardTitle>Dépenses par catégorie / Expenses by Category</CardTitle>
              </CardHeader>
              <CardContent>
                {pieData.length === 0 ? (
                  <p className="text-sm text-gray-400 py-10 text-center">Aucune dépense enregistrée</p>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) =>
                          `${name} ${(percent * 100).toFixed(0)}%`
                        }
                        outerRadius={80}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#fff",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                        }}
                        formatter={(v: number) => formatTND(v)}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Top clients table */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Clients fidèles / Top Clients</CardTitle>
              <Button variant="outline" size="sm">Voir tout</Button>
            </CardHeader>
            <CardContent>
              {clients.length === 0 ? (
                <p className="text-sm text-gray-400 py-6 text-center">Aucun client trouvé</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Client ID</TableHead>
                      <TableHead>Nb Factures</TableHead>
                      <TableHead className="text-right">CA Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {clients.map((c, i) => (
                      <TableRow key={c.client_id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <span className={`w-5 h-5 rounded-full text-xs font-bold flex items-center justify-center text-white ${
                              i === 0 ? "bg-yellow-400" :
                              i === 1 ? "bg-gray-400" :
                              i === 2 ? "bg-amber-600" : "bg-blue-400"
                            }`}>
                              {i + 1}
                            </span>
                            Client #{c.client_id}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{c.nb_factures} factures</Badge>
                        </TableCell>
                        <TableCell className="text-right font-semibold text-green-700">
                          {formatTND(c.ca_total)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Summary row */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border-green-200 bg-green-50">
                <CardContent className="p-4">
                  <p className="text-xs text-green-700 font-semibold uppercase tracking-wide mb-1">
                    Revenus encaissés
                  </p>
                  <p className="text-xl font-bold text-green-800">{formatTND(stats.revenus)}</p>
                </CardContent>
              </Card>
              <Card className="border-red-200 bg-red-50">
                <CardContent className="p-4">
                  <p className="text-xs text-red-700 font-semibold uppercase tracking-wide mb-1">
                    Dépenses payées
                  </p>
                  <p className="text-xl font-bold text-red-800">{formatTND(stats.depenses)}</p>
                </CardContent>
              </Card>
              <Card className={`${stats.profit >= 0 ? "border-blue-200 bg-blue-50" : "border-red-200 bg-red-50"}`}>
                <CardContent className="p-4">
                  <p className="text-xs text-blue-700 font-semibold uppercase tracking-wide mb-1">
                    Marge nette
                  </p>
                  <p className={`text-xl font-bold ${stats.profit >= 0 ? "text-blue-800" : "text-red-800"}`}>
                    {formatTND(stats.profit)}
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
}
