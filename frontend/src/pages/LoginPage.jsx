import { useState } from "react";
import { api } from "../lib/api.js";
import { useToast } from "../hooks/useToast.jsx";

export default function LoginPage({ onLogin }) {
  const toast  = useToast();
  const [tab,  setTab]  = useState("login");
  const [form, setForm] = useState({
    email: "", password: "", name: "",
    firm_name: "", admin_email: "", role: "Admin",
  });
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  async function submit() {
    if (!form.email || !form.password) {
      toast("Email and password are required.", "warning");
      return;
    }

    setLoading(true);
    const path = tab === "login" ? "/auth/login" : "/auth/signup";

    const body =
      tab === "login"
        ? { email: form.email, password: form.password }
        : {
            email:       form.email,
            password:    form.password,
            name:        form.name,
            role:        form.role,
            firm_name:   form.role === "Admin" ? form.firm_name  : "",
            admin_email: form.role === "Clerk" ? form.admin_email : "",
          };

    const { data, error } = await api.post(path, body);

    if (error) {
      toast(error, "error");
      setLoading(false);
      return;
    }

    if (data?.access_token) {
      localStorage.setItem("cai_token", data.access_token);

      // Fetch user profile using the new token
      const { data: me } = await api.get("/auth/me");
      if (me) {
        localStorage.setItem("cai_user", JSON.stringify(me));
        onLogin(data.access_token, me);
      } else {
        onLogin(data.access_token, { email: form.email });
      }
    } else {
      toast("Unexpected response from server.", "error");
    }

    setLoading(false);
  }

  const isClerk = form.role === "Clerk";

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
      }}
    >
      {/* Subtle grid texture */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          backgroundImage: `
            linear-gradient(var(--border) 1px, transparent 1px),
            linear-gradient(90deg, var(--border) 1px, transparent 1px)
          `,
          backgroundSize: "40px 40px",
          opacity: 0.3,
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "100%", maxWidth: 360, position: "relative" }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "baseline",
              gap: 2,
              marginBottom: 8,
            }}
          >
            <span
              style={{
                fontSize: 32,
                fontWeight: 700,
                letterSpacing: "-0.04em",
                color: "var(--text)",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              CA
            </span>
            <span
              style={{
                fontSize: 32,
                fontWeight: 700,
                letterSpacing: "-0.04em",
                color: "var(--accent)",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              I
            </span>
          </div>
          <div style={{ fontSize: 13, color: "var(--text-3)" }}>
            Autonomous GST Compliance
          </div>
        </div>

        <div className="card" style={{ padding: 28 }}>
          {/* Tab switcher */}
          <div
            style={{
              display: "flex",
              background: "var(--surface-2)",
              borderRadius: 6,
              padding: 3,
              marginBottom: 24,
            }}
          >
            {["login", "signup"].map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); }}
                style={{
                  flex: 1,
                  padding: "7px 0",
                  borderRadius: 4,
                  border: "none",
                  cursor: "pointer",
                  fontSize: 12.5,
                  fontWeight: 500,
                  fontFamily: "inherit",
                  background: tab === t ? "var(--surface-3)" : "transparent",
                  color: tab === t ? "var(--text)" : "var(--text-2)",
                  transition: "all 0.15s",
                  textTransform: "capitalize",
                }}
              >
                {t === "login" ? "Sign In" : "Create Account"}
              </button>
            ))}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {/* Sign-up only fields */}
            {tab === "signup" && (
              <>
                <div>
                  <label className="label">Full Name</label>
                  <input
                    className="input"
                    value={form.name}
                    onChange={set("name")}
                    placeholder="Your Name"
                  />
                </div>
                <div>
                  <label className="label">Role</label>
                  <select
                    className="input"
                    value={form.role}
                    onChange={set("role")}
                    style={{ cursor: "pointer" }}
                  >
                    <option value="Admin">Admin — Create a new CA Firm</option>
                    <option value="Clerk">Clerk — Join an existing CA Firm</option>
                  </select>
                </div>
                {!isClerk ? (
                  <div>
                    <label className="label">Firm Name</label>
                    <input
                      className="input"
                      value={form.firm_name}
                      onChange={set("firm_name")}
                      placeholder="Raj Associates"
                    />
                  </div>
                ) : (
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        color: "var(--accent)",
                        marginBottom: 6,
                      }}
                    >
                      Firm Admin Email (to link your account)
                    </label>
                    <input
                      className="input"
                      value={form.admin_email}
                      onChange={set("admin_email")}
                      placeholder="admin@firm.com"
                      style={{ borderColor: "var(--accent-border)" }}
                    />
                  </div>
                )}
              </>
            )}

            {/* Common fields */}
            <div>
              <label className="label">Email</label>
              <input
                className="input"
                type="email"
                value={form.email}
                onChange={set("email")}
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                className="input"
                type="password"
                value={form.password}
                onChange={set("password")}
                placeholder="••••••••"
                onKeyDown={(e) => e.key === "Enter" && submit()}
              />
            </div>

            <button
              onClick={submit}
              disabled={loading}
              className="btn btn-primary btn-lg"
              style={{ width: "100%", marginTop: 4 }}
            >
              {loading
                ? "Please wait..."
                : tab === "login"
                ? "Sign In"
                : "Create Account"}
            </button>
          </div>
        </div>

        <div
          style={{
            textAlign: "center",
            marginTop: 20,
            fontSize: 11.5,
            color: "var(--text-3)",
          }}
        >
          CAI &mdash; Python Charmers &middot; TCET
        </div>
      </div>
    </div>
  );
}
