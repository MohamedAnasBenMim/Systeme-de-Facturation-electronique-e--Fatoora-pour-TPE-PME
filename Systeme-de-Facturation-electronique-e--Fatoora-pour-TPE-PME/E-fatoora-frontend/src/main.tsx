import { createRoot } from "react-dom/client";
import App from "./app/App.tsx";
import "./styles/index.css";
import { ClerkProvider } from "@clerk/clerk-react";
import { frFR } from "@clerk/localizations"; 
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const root = createRoot(document.getElementById("root")!);

if (PUBLISHABLE_KEY) {
  root.render(
    <ClerkProvider publishableKey={PUBLISHABLE_KEY} localization={frFR}>
      <App />
    </ClerkProvider>
  );
} else {
  root.render(<App />);
}
