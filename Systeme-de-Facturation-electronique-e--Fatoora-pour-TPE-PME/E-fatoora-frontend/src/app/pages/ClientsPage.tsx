import { useState, useEffect } from "react";
import {
  getClients,
  deleteClient,
  createClient,
  updateClient,
} from "../../services/clientService";
import { Plus, Search, Mail, Phone, Building2, Edit, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "../components/ui/table";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "../components/ui/dialog";

type Client = {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  adresse: string;
  matricule_fiscal: string;
};

const emptyForm = {
  nom: "",
  prenom: "",
  email: "",
  telephone: "",
  adresse: "",
  matricule_fiscal: "",
};

type ClientListResponse = {
  total: number;
  clients: Client[];
};

export function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const data: ClientListResponse = await getClients();
      setClients(data.clients);
      setError(null);
    } catch (err) {
      console.error("ERROR:", err);
      setError("Erreur lors du chargement des clients.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  useEffect(() => {
    if (editingClient) {
      setFormData({
        nom: editingClient.nom,
        prenom: editingClient.prenom,
        email: editingClient.email,
        telephone: editingClient.telephone,
        adresse: editingClient.adresse,
        matricule_fiscal: editingClient.matricule_fiscal,
      });
    } else {
      setFormData(emptyForm);
    }
  }, [editingClient]);

  // ✅ FIX : handleChange utilise e.target.name au lieu de e.target.id
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    // ✅ Validation basique avant envoi
    if (!formData.nom.trim() || !formData.email.trim()) {
      setError("Le nom et l'email sont obligatoires.");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      if (editingClient) {
        await updateClient(editingClient.id, formData);
      } else {
        await createClient(formData);
      }
      await fetchClients();
      closeDialog();
    } catch (err) {
      setError("Erreur lors de la sauvegarde du client.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Supprimer ce client ?")) return;
    try {
      await deleteClient(id);
      setClients((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      setError("Erreur lors de la suppression.");
    }
  };

  const closeDialog = () => {
    setIsAddDialogOpen(false);
    setEditingClient(null);
    setFormData(emptyForm);
    setError(null);
  };

  const filteredClients = clients.filter((c) =>
    [c.nom, c.prenom, c.email].some((field) =>
      field?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
          <p className="text-gray-500 mt-1">Manage your client information</p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Client
        </Button>
      </div>

      {error && !isAddDialogOpen && editingClient === null && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>All Clients</CardTitle>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="search"
                placeholder="Search clients..."
                className="pl-10 w-64"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-10 text-gray-400">Chargement...</div>
          ) : filteredClients.length === 0 ? (
            <div className="text-center py-10 text-gray-400">Aucun client trouvé.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nom</TableHead>
                  <TableHead>Prénom</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Téléphone</TableHead>
                  <TableHead>Adresse</TableHead>
                  <TableHead>Matricule Fiscale</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClients.map((client) => (
                  <TableRow key={client.id}>
                    <TableCell className="font-medium">{client.nom}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Building2 className="w-4 h-4 text-gray-400" />
                        {client.prenom}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Mail className="w-4 h-4 text-gray-400" />
                        {client.email}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4 text-gray-400" />
                        {client.telephone}
                      </div>
                    </TableCell>
                    <TableCell>{client.adresse}</TableCell>
                    <TableCell className="font-mono text-sm">{client.matricule_fiscal}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setEditingClient(client)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(client.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
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

      {/* ✅ Dialog Add / Edit */}
      <Dialog
        open={isAddDialogOpen || editingClient !== null}
        onOpenChange={(open) => { if (!open) closeDialog(); }}
      >
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingClient ? "Modifier Client" : "Ajouter Client"}
            </DialogTitle>
          </DialogHeader>

          {/* ✅ Erreur visible dans le dialog */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                {/* ✅ FIX : name="nom" correspond à la clé formData */}
                <Label htmlFor="nom">Nom *</Label>
                <Input
                  id="nom"
                  name="nom"
                  placeholder="ex: Ben Salah"
                  value={formData.nom}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                {/* ✅ FIX : name="prenom" correspond à la clé formData */}
                <Label htmlFor="prenom">Prénom *</Label>
                <Input
                  id="prenom"
                  name="prenom"
                  placeholder="ex: Mohamed"
                  value={formData.prenom}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                {/* ✅ FIX : name="email" */}
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="contact@company.tn"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                {/* ✅ FIX : name="telephone" */}
                <Label htmlFor="telephone">Téléphone *</Label>
                <Input
                  id="telephone"
                  name="telephone"
                  type="tel"
                  placeholder="+216 71 XXX XXX"
                  value={formData.telephone}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="space-y-2">
              {/* ✅ FIX : name="adresse" */}
              <Label htmlFor="adresse">Adresse</Label>
              <Input
                id="adresse"
                name="adresse"
                placeholder="ex: Avenue Habib Bourguiba, Tunis"
                value={formData.adresse}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              {/* ✅ FIX : name="matricule_fiscal" */}
              <Label htmlFor="matricule_fiscal">Matricule Fiscale</Label>
              <Input
                id="matricule_fiscal"
                name="matricule_fiscal"
                placeholder="ex: 0123456A"
                value={formData.matricule_fiscal}
                onChange={handleChange}
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t">
              <Button variant="outline" onClick={closeDialog} disabled={submitting}>
                Annuler
              </Button>
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting
                  ? "Sauvegarde..."
                  : editingClient
                  ? "Mettre à jour"
                  : "Ajouter"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}