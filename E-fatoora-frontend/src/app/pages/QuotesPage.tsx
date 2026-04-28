import { FileEdit, Calendar } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";

export function QuotesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Quotes / Devis</h1>
        <p className="text-gray-500 mt-1">Create and manage quotes for clients</p>
      </div>

      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-16">
          <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
            <FileEdit className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No quotes yet / Aucun devis
          </h3>
          <p className="text-gray-500 text-center max-w-md mb-6">
            Create your first quote to send estimates to your clients before invoicing.
          </p>
          <Button>
            <FileEdit className="w-4 h-4 mr-2" />
            Create First Quote
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
