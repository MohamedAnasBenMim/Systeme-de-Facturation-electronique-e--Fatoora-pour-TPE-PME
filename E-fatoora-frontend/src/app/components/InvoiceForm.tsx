import { useState } from "react";
import { Plus, Trash2, Send } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Card, CardContent } from "./ui/card";

const clients = [
  "STEG Tunisie",
  "Orange Tunisie",
  "Tunisie Telecom",
  "Amen Bank",
  "BH Bank",
  "SONEDE",
  "Tunisair",
  "Topnet",
];

const products = [
  { name: "Web Development", price: 2500 },
  { name: "Mobile App Development", price: 4000 },
  { name: "UI/UX Design", price: 1500 },
  { name: "Consulting Services", price: 1000 },
  { name: "SEO Optimization", price: 800 },
  { name: "Cloud Hosting", price: 500 },
];

interface LineItem {
  id: string;
  product: string;
  description: string;
  quantity: number;
  price: number;
}

interface InvoiceFormProps {
  onClose: () => void;
}

export function InvoiceForm({ onClose }: InvoiceFormProps) {
  const [selectedClient, setSelectedClient] = useState("");
  const [lineItems, setLineItems] = useState<LineItem[]>([
    { id: "1", product: "", description: "", quantity: 1, price: 0 },
  ]);

  const addLineItem = () => {
    setLineItems([
      ...lineItems,
      {
        id: Date.now().toString(),
        product: "",
        description: "",
        quantity: 1,
        price: 0,
      },
    ]);
  };

  const removeLineItem = (id: string) => {
    if (lineItems.length > 1) {
      setLineItems(lineItems.filter((item) => item.id !== id));
    }
  };

  const updateLineItem = (id: string, field: keyof LineItem, value: any) => {
    setLineItems(
      lineItems.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const calculateSubtotal = () => {
    return lineItems.reduce((sum, item) => sum + item.quantity * item.price, 0);
  };

  const calculateTVA = () => {
    return calculateSubtotal() * 0.2; // 20% TVA
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTVA();
  };

  return (
    <div className="space-y-6">
      {/* Client Selection */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="client">Client / Client</Label>
          <Select value={selectedClient} onValueChange={setSelectedClient}>
            <SelectTrigger id="client">
              <SelectValue placeholder="Select a client..." />
            </SelectTrigger>
            <SelectContent>
              {clients.map((client) => (
                <SelectItem key={client} value={client}>
                  {client}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="date">Invoice Date / Date de facture</Label>
          <Input id="date" type="date" defaultValue={new Date().toISOString().split('T')[0]} />
        </div>
      </div>

      {/* Line Items */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label>Products / Services</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={addLineItem}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Line
          </Button>
        </div>

        <div className="space-y-3">
          {lineItems.map((item, index) => (
            <Card key={item.id}>
              <CardContent className="p-4">
                <div className="grid grid-cols-12 gap-3 items-end">
                  <div className="col-span-4 space-y-2">
                    <Label className="text-xs">Product / Service</Label>
                    <Select
                      value={item.product}
                      onValueChange={(value) => {
                        updateLineItem(item.id, "product", value);
                        const selectedProduct = products.find(
                          (p) => p.name === value
                        );
                        if (selectedProduct) {
                          updateLineItem(item.id, "price", selectedProduct.price);
                        }
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select..." />
                      </SelectTrigger>
                      <SelectContent>
                        {products.map((product) => (
                          <SelectItem key={product.name} value={product.name}>
                            {product.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="col-span-3 space-y-2">
                    <Label className="text-xs">Description</Label>
                    <Input
                      value={item.description}
                      onChange={(e) =>
                        updateLineItem(item.id, "description", e.target.value)
                      }
                      placeholder="Optional details..."
                    />
                  </div>

                  <div className="col-span-2 space-y-2">
                    <Label className="text-xs">Quantity / Qté</Label>
                    <Input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) =>
                        updateLineItem(
                          item.id,
                          "quantity",
                          parseInt(e.target.value) || 1
                        )
                      }
                    />
                  </div>

                  <div className="col-span-2 space-y-2">
                    <Label className="text-xs">Price / Prix (TND)</Label>
                    <Input
                      type="number"
                      min="0"
                      step="0.01"
                      value={item.price}
                      onChange={(e) =>
                        updateLineItem(
                          item.id,
                          "price",
                          parseFloat(e.target.value) || 0
                        )
                      }
                    />
                  </div>

                  <div className="col-span-1 flex items-center justify-center">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeLineItem(item.id)}
                      disabled={lineItems.length === 1}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Totals */}
      <Card className="bg-gray-50">
        <CardContent className="p-6">
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal (HT):</span>
              <span className="font-medium">
                {calculateSubtotal().toFixed(2)} TND
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">TVA (20%):</span>
              <span className="font-medium">
                {calculateTVA().toFixed(2)} TND
              </span>
            </div>
            <div className="border-t border-gray-300 pt-3">
              <div className="flex justify-between">
                <span className="font-semibold text-gray-900">
                  Total (TTC):
                </span>
                <span className="text-2xl font-bold text-blue-600">
                  {calculateTotal().toFixed(2)} TND
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t">
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="outline">Save Draft / Brouillon</Button>
        <Button>
          <Send className="w-4 h-4 mr-2" />
          Save & Send / Enregistrer et envoyer
        </Button>
      </div>
    </div>
  );
}
