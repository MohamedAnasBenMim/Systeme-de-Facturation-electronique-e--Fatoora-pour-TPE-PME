import { createBrowserRouter, Navigate } from "react-router";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { InvoicesPage } from "./pages/InvoicesPage";
import { ClientsPage } from "./pages/ClientsPage";
import { QuotesPage } from "./pages/QuotesPage";
import { ExpensesPage } from "./pages/ExpensesPage";
import ProductsPage from "./pages/ProductsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { LoginPage } from "./pages/LoginPage";
import FacturePage from "./pages/FacturePage";
import LandingPage from "./pages/LandingPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import CompteBancairePage from "./pages/CompteBancairePage";
import { SSOCallback } from "./pages/SSOCallback";
import TvaPage from "./pages/TvaPage";

export const router = createBrowserRouter([
  // Page d’accueil (non protégée)
  {
    path: "/Acceuil",
    Component: LandingPage,
  },

  // Login / SSO (non protégés)
  {
    path: "login",
    Component: LoginPage,
  },
  {
    path: "sso-callback",
    Component: SSOCallback,
  },

  // Routes protégées — dans le Layout
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      
      { index: true, element: <Navigate to="/Acceuil" replace /> },
      { path: "facture", Component: FacturePage },
      { path: "dashboard", Component: DashboardPage },
      { path: "invoices", Component: InvoicesPage },
      { path: "clients", Component: ClientsPage },
      { path: "quotes", Component: QuotesPage },
      { path: "expenses", Component: ExpensesPage },
      { path: "products", Component: ProductsPage },
      { path: "reports", Component: ReportsPage },
      { path: "settings", Component: SettingsPage },
      { path: "compte", Component: CompteBancairePage },
      { path: "parametres", Component: TvaPage },
    ],
  },

  // Redirection par défaut vers la page d’accueil
  // / -> /Acceuil
  {
    path: "*",
    element: <Navigate to="/Acceuil" replace />,
  },
]);