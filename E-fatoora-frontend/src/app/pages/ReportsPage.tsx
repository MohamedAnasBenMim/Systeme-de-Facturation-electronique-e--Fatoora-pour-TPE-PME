import { BarChart3 } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";

export function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Reports / Rapports
        </h1>
        <p className="text-gray-500 mt-1">View business analytics and financial reports</p>
      </div>

      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-16">
          <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mb-4">
            <BarChart3 className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Reports coming soon / Rapports bientôt disponibles
          </h3>
          <p className="text-gray-500 text-center max-w-md mb-6">
            Advanced analytics and reporting features will be available soon.
          </p>
          <Button variant="outline">Learn More</Button>
        </CardContent>
      </Card>
    </div>
  );
}
