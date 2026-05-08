// src/pages/SSOCallback.tsx
import { AuthenticateWithRedirectCallback } from "@clerk/clerk-react";

export function SSOCallback() {
  return <AuthenticateWithRedirectCallback />;
}