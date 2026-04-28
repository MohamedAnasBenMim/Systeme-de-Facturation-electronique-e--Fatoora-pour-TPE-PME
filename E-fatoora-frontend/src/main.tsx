import { createRoot } from "react-dom/client";
import App from "./app/App.tsx";
import "./styles/index.css";
import { ClerkProvider } from "@clerk/clerk-react";
import { frFR } from "@clerk/localizations"; 
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Clerk Publishable Key manquante dans .env");
}

createRoot(document.getElementById("root")!).render(
  <ClerkProvider 
    publishableKey={PUBLISHABLE_KEY}
    localization={frFR}          // popup Google en français
  >
    <App />
  </ClerkProvider>
);