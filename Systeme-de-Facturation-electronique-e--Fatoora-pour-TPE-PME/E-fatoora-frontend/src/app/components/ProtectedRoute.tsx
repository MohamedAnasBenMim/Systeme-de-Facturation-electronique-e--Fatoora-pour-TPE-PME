import { Navigate } from "react-router";
import { isAuthenticated } from "../../services/authService";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}