import { Wallet } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";

export function ExpensesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Expenses / Dépenses
        </h1>
        <p className="text-gray-500 mt-1">Track and manage your business expenses</p>
      </div>

      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-16">
          <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-4">
            <Wallet className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No expenses tracked / Aucune dépense
          </h3>
          <p className="text-gray-500 text-center max-w-md mb-6">
            Start tracking your business expenses to monitor cash flow and profitability.
          </p>
          <Button>
            <Wallet className="w-4 h-4 mr-2" />
            Add Expense
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
