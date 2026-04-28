import { useState, useEffect } from "react";
import { Plus, Search, Filter, Download, Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import factureService from "../../services/factureService";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { InvoiceForm } from "../components/InvoiceForm";

export function InvoicesPage() {
  const [factures, setFactures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  useEffect(() => {
    loadFactures();
  }, []);

  const loadFactures = async () => {
    try {
      setLoading(true);
      const data = await factureService.getAll(1, 10);
      setFactures(Array.isArray(data) ? data : data.data || []);
    } catch (error) {
      console.error("Erreur chargement factures:", error);
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async (id: number) => {
    try {
      const blob = await factureService.downloadPdf(id);
      const contentDisposition = blob.headers?.["content-disposition"] || "";
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      const filename = filenameMatch ? filenameMatch[1] : `facture_${id}.pdf`;

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("❌ Erreur PDF:", error);
    }
  };

  const previewPdf = async (id: number) => {
    try {
      const token = localStorage.getItem("token");

      const response = await fetch(
        `http://localhost:8000/api/v1/factures/${id}/pdf/preview`,
        {
          method: "GET",
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Impossible de charger le PDF");
      }

      const blob = await response.blob();
      const pdfUrl = window.URL.createObjectURL(blob);
      window.open(pdfUrl, "_blank");
    } catch (error) {
      console.error("Erreur preview PDF:", error);
    }
  };

  const handleFactureCreated = () => {
    setIsCreateDialogOpen(false);
    loadFactures();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Invoices / Factures</h1>
          <p className="text-gray-500 mt-1">Manage and track all your invoices</p>
        </div>

        <Button onClick={() => (window.location.href = "/facture")}>
          <Plus className="w-4 h-4 mr-2" />
          Create Invoice
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>All Invoices</CardTitle>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search invoices..."
                  className="pl-10 w-64"
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-lg text-gray-500">Chargement des factures...</div>
            </div>
          ) : factures.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              Aucune facture trouvée
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Numéro</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Date creation</TableHead>
                  <TableHead>Date Échéance</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead className="text-right">HT</TableHead>
                  <TableHead className="text-right">TVA</TableHead>
                  <TableHead className="text-right">TTC</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {factures.map((facture: any) => (
                  <TableRow key={facture.id}>
                    <TableCell className="font-medium">
                      FACT-{facture.id.toString().padStart(4, "0")}
                    </TableCell>
                    <TableCell>{facture.client?.email || "Client inconnu"}</TableCell>
                    <TableCell>
                      {facture.date_creation
                        ? new Date(facture.date_creation).toLocaleDateString("fr-TN")
                        : "-"}
                    </TableCell>
                    <TableCell>
                      {new Date(facture.date_echeance).toLocaleDateString("fr-TN")}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          facture.statut === "payee"
                            ? "default"
                            : facture.statut === "brouillon"
                            ? "secondary"
                            : "destructive"
                        }
                        className={
                          facture.statut === "payee"
                            ? "bg-green-100 text-green-700"
                            : facture.statut === "brouillon"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-red-100 text-red-700"
                        }
                      >
                        {facture.statut === "payee"
                          ? "Payée"
                          : facture.statut === "brouillon"
                          ? "Brouillon"
                          : "Brouillon"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {facture.total_ht?.toFixed(3) || 0} TND
                    </TableCell>
                    <TableCell className="text-right">
                      {facture.total_tva?.toFixed(3) || 0} TND
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {facture.total_ttc?.toFixed(3) || 0} TND
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => previewPdf(facture.id)}
                          title="Prévisualiser"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => downloadPdf(facture.id)}
                          title="Télécharger PDF"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Invoice / Créer une facture</DialogTitle>
          </DialogHeader>
          <InvoiceForm
            onClose={() => setIsCreateDialogOpen(false)}
            onSuccess={handleFactureCreated}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}