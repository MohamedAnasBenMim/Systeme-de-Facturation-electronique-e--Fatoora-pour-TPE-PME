import { useState } from "react";
import { useNavigate } from "react-router";
import { login } from "../../services/authService";
import { useSignIn, useUser } from "@clerk/clerk-react";
import { useEffect } from "react";
import api from "../../services/api";

/* ─────────────────────────────────────────
   Palette Be CarthAI
   --bc-dark      : #2E2840  (deep indigo‑noir)
   --bc-purple    : #63529B  (violet logo "AI")
   --bc-purple-lt : #3D3558  (hover bouton)
   --bc-silver    : #8A83A3  (gris argenté)
   --bc-bg        : #F5F4F7  (fond page)
   --bc-panel     : #EEEDF3  (fond panneau gauche)
   --bc-border    : #D9D4EA  (bordures)
   --bc-muted     : #C4BEDD  (placeholders)
───────────────────────────────────────── */

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    display: "flex",
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
    background: "#F5F4F7",
  },

  /* ── Panneau gauche ── */
  leftPanel: {
    width: "42%",
    background: "#EEEDF3",
    borderRight: "1px solid #DDDAE6",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "2.5rem 2.25rem 2rem",
    position: "relative",
    overflow: "hidden",
  },

  brand: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: "8px",
    position: "relative",
    zIndex: 1,
  },

  brandSymbol: { width: 52, height: 52 },

  brandName: {
    fontFamily: "'Cinzel', 'Georgia', serif",
    fontSize: "17px",
    fontWeight: 600,
    color: "#2E2840",
    letterSpacing: "1px",
    lineHeight: 1.2,
  },

  brandNameAI: { color: "#63529B" },

  brandSub: {
    fontSize: "10px",
    letterSpacing: "3px",
    color: "#8A83A3",
    fontWeight: 500,
    textTransform: "uppercase" as const,
  },

  heroText: { position: "relative", zIndex: 1 },

  heroTitle: {
    fontFamily: "'Cinzel', 'Georgia', serif",
    fontSize: "20px",
    fontWeight: 600,
    color: "#2E2840",
    lineHeight: 1.45,
    marginBottom: "10px",
  },

  heroBody: {
    fontSize: "13px",
    color: "#6B6585",
    lineHeight: 1.7,
  },

  features: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
    position: "relative",
    zIndex: 1,
  },

  featureItem: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    fontSize: "12.5px",
    color: "#5A5478",
  },

  featDot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
    background: "#63529B",
    flexShrink: 0,
  },

  /* ── Panneau droit ── */
  rightPanel: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "2rem",
  },

  loginCard: {
    background: "white",
    borderRadius: "18px",
    padding: "2.5rem 2.25rem",
    width: "100%",
    maxWidth: "380px",
    border: "1px solid #E3DFF0",
    boxShadow: "0 2px 24px rgba(46,40,64,0.07)",
  },

  silverBadge: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "#EEEDF3",
    border: "1px solid #D9D4EA",
    borderRadius: "20px",
    padding: "4px 12px",
    fontSize: "11px",
    color: "#5A5478",
    fontWeight: 500,
    letterSpacing: "0.3px",
    marginBottom: "1.5rem",
  },

  badgeDot: {
    width: "5px",
    height: "5px",
    borderRadius: "50%",
    background: "#63529B",
  },

  cardTitle: {
    fontFamily: "'Cinzel', 'Georgia', serif",
    fontSize: "20px",
    fontWeight: 600,
    color: "#2E2840",
    marginBottom: "4px",
  },

  subtitle: {
    fontSize: "13px",
    color: "#8A83A3",
    marginBottom: "1.75rem",
  },

  errorBox: {
    background: "#FEF2F2",
    border: "1px solid #FECACA",
    color: "#B91C1C",
    padding: "10px 14px",
    borderRadius: "10px",
    fontSize: "13px",
    marginBottom: "1.25rem",
  },

  field: { marginBottom: "1rem" },

  label: {
    display: "block",
    fontSize: "12.5px",
    fontWeight: 500,
    color: "#4A4465",
    marginBottom: "6px",
    letterSpacing: "0.2px",
  },

  input: {
    width: "100%",
    height: "42px",
    padding: "0 14px",
    borderRadius: "10px",
    border: "1px solid #D9D4EA",
    fontSize: "14px",
    fontFamily: "inherit",
    color: "#2E2840",
    background: "#FAF9FC",
    outline: "none",
  },

  inputFocused: {
    borderColor: "#63529B",
    boxShadow: "0 0 0 3px rgba(99,82,155,0.13)",
    background: "white",
  },

  forgot: {
    textAlign: "right" as const,
    marginTop: "-6px",
    marginBottom: "1.25rem",
  },

  forgotLink: {
    fontSize: "12px",
    color: "#63529B",
    textDecoration: "none",
    background: "none",
    border: "none",
    cursor: "pointer",
    fontFamily: "inherit",
  },

  btnPrimary: {
    width: "100%",
    height: "44px",
    background: "#2E2840",
    color: "white",
    border: "none",
    borderRadius: "11px",
    fontSize: "14px",
    fontWeight: 600,
    fontFamily: "inherit",
    cursor: "pointer",
    letterSpacing: "0.2px",
    transition: "background 0.15s",
  },

  btnPrimaryHover: { background: "#3D3558" },

  dividerWrap: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    margin: "1.25rem 0",
  },

  dividerLine: { flex: 1, height: "1px", background: "#EAE6F4" },

  dividerText: { fontSize: "12px", color: "#C4BEDD", whiteSpace: "nowrap" as const },

  btnGoogle: {
    width: "100%",
    height: "42px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    background: "#F5F3FA",
    border: "1px solid #D9D4EA",
    borderRadius: "11px",
    fontSize: "13.5px",
    fontWeight: 500,
    color: "#4A4465",
    fontFamily: "inherit",
    cursor: "pointer",
  },

  footerNote: {
    marginTop: "1.5rem",
    textAlign: "center" as const,
    fontSize: "11.5px",
    color: "#B5ACCC",
  },
};

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [pwFocus, setPwFocus] = useState(false);
  const [emailFocus, setEmailFocus] = useState(false);
  const [btnHover, setBtnHover] = useState(false);

  const { signIn, isLoaded } = useSignIn();
  const { user, isSignedIn } = useUser();

  useEffect(() => {
    if (isSignedIn && user) handleClerkTokenExchange();
  }, [isSignedIn, user]);

  const handleClerkTokenExchange = async () => {
    try {
      setGoogleLoading(true);
      const clerkToken =
        (await signIn?.client?.activeSessions?.[0]?.getToken()) ?? null;
      if (!clerkToken) throw new Error("Token Clerk introuvable");
      const { data } = await api.post("/auth/clerk/token", {
        clerk_token: clerkToken,
      });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      navigate("/dashboard");
    } catch {
      setError("Erreur de connexion avec Google. Réessayez.");
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (!isLoaded) return;
    try {
      setGoogleLoading(true);
      await signIn.authenticateWithRedirect({
        strategy: "oauth_google",
        redirectUrl: "/sso-callback",
        redirectUrlComplete: "/dashboard",
      });
    } catch {
      setError("Impossible de se connecter avec Google.");
      setGoogleLoading(false);
    }
  };

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("Email ou mot de passe incorrect.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      {/* ── Panneau gauche ── */}
      <div style={styles.leftPanel}>
        {/* Logo Be CarthAI */}
        <div style={styles.brand}>
          <svg style={styles.brandSymbol} viewBox="0 0 52 52" fill="none">
            <circle cx="26" cy="10" r="6" stroke="#63529B" strokeWidth="2.5" />
            <line x1="13" y1="18" x2="39" y2="18" stroke="#8A83A3" strokeWidth="2.5" strokeLinecap="round" />
            <polygon
              points="26,44 12,20 40,20"
              stroke="#63529B"
              strokeWidth="2.5"
              fill="none"
              strokeLinejoin="round"
            />
          </svg>
          <div>
            <div style={styles.brandName}>
              BE CARTH<span style={styles.brandNameAI}>AI</span>
            </div>
            <div style={styles.brandSub}>Consulting</div>
          </div>
        </div>

        {/* Texte héro */}
        <div style={styles.heroText}>
          <h2 style={styles.heroTitle}>
            Votre facturation,<br />réinventée par l'IA
          </h2>
          <p style={styles.heroBody}>
            Une solution intelligente pour gérer, automatiser et optimiser vos
            factures — propulsée par Be CarthAI Consulting.
          </p>
        </div>

        {/* Features */}
        <div style={styles.features}>
          {[
            "Facturation automatisée et intelligente",
            "Conformité fiscale garantie",
            "Suivi des paiements en temps réel",
            "Rapports et analyses avancés",
          ].map((f) => (
            <div key={f} style={styles.featureItem}>
              <div style={styles.featDot} />
              {f}
            </div>
          ))}
        </div>
      </div>

      {/* ── Panneau droit ── */}
      <div style={styles.rightPanel}>
        <div style={styles.loginCard}>
          {/* Badge */}
          <div style={styles.silverBadge}>
            <div style={styles.badgeDot} />
            Espace sécurisé
          </div>

          <h1 style={styles.cardTitle}>Connexion</h1>
          <p style={styles.subtitle}>
            Accédez à votre tableau de bord de facturation
          </p>

          {error && <div style={styles.errorBox}>{error}</div>}

          {/* Email */}
          <div style={styles.field}>
            <label style={styles.label}>Adresse e-mail</label>
            <input
              type="email"
              placeholder="vous@becarthai.tn"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setEmailFocus(true)}
              onBlur={() => setEmailFocus(false)}
              style={{
                ...styles.input,
                ...(emailFocus ? styles.inputFocused : {}),
              }}
            />
          </div>

          {/* Mot de passe */}
          <div style={styles.field}>
            <label style={styles.label}>Mot de passe</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setPwFocus(true)}
              onBlur={() => setPwFocus(false)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              style={{
                ...styles.input,
                ...(pwFocus ? styles.inputFocused : {}),
              }}
            />
          </div>

          {/* Mot de passe oublié */}
          <div style={styles.forgot}>
            <button style={styles.forgotLink}>Mot de passe oublié ?</button>
          </div>

          {/* Bouton connexion */}
          <button
            onClick={handleLogin}
            disabled={loading}
            onMouseEnter={() => setBtnHover(true)}
            onMouseLeave={() => setBtnHover(false)}
            style={{
              ...styles.btnPrimary,
              ...(btnHover && !loading ? styles.btnPrimaryHover : {}),
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? "Connexion..." : "Se connecter"}
          </button>

          {/* Séparateur */}
          <div style={styles.dividerWrap}>
            <div style={styles.dividerLine} />
            <span style={styles.dividerText}>ou</span>
            <div style={styles.dividerLine} />
          </div>

          {/* Bouton Google */}
          <button
            onClick={handleGoogleLogin}
            disabled={googleLoading || !isLoaded}
            style={{ ...styles.btnGoogle, opacity: googleLoading || !isLoaded ? 0.6 : 1 }}
          >
            <svg width="18" height="18" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.14 0 5.95 1.08 8.17 2.85l6.08-6.08C34.5 3.02 29.6 1 24 1 14.82 1 7.07 6.48 3.87 14.22l7.07 5.49C12.6 13.39 17.85 9.5 24 9.5z" />
              <path fill="#4285F4" d="M46.1 24.5c0-1.64-.15-3.22-.42-4.75H24v9h12.42c-.54 2.9-2.18 5.36-4.64 7.01l7.19 5.59C43.18 37.22 46.1 31.3 46.1 24.5z" />
              <path fill="#FBBC05" d="M10.94 28.29A14.6 14.6 0 0 1 9.5 24c0-1.49.26-2.93.72-4.29L3.15 14.22A23.94 23.94 0 0 0 0 24c0 3.86.92 7.5 2.54 10.73l8.4-6.44z" />
              <path fill="#34A853" d="M24 47c5.97 0 10.98-1.97 14.64-5.36l-7.19-5.59C29.55 37.67 26.93 38.5 24 38.5c-6.14 0-11.38-3.88-13.24-9.35l-7.22 5.58C7.22 42.35 15.05 47 24 47z" />
            </svg>
            {googleLoading ? "Redirection..." : "Continuer avec Google"}
          </button>

          <p style={styles.footerNote}>
            En vous connectant, vous acceptez les conditions d'utilisation.
          </p>
        </div>
      </div>
    </div>
  );
}