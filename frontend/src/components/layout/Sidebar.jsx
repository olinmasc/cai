import {
  LayoutDashboard, Users, AlertTriangle,
  Activity, FileText, LogOut
} from "lucide-react";

const NAV = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "clients", label: "Clients", icon: Users },
  { id: "filings", label: "Filings", icon: FileText },
  { id: "exceptions", label: "Exceptions", icon: AlertTriangle },
  { id: "agents", label: "Agent Status", icon: Activity },
];

export default function Sidebar({ view, setView, user, onLogout }) {
  const initial = (user?.name || "U")[0].toUpperCase();
  const isAdmin = user?.role === "Admin";

  return (
    <aside
      style={{
        width: 260,
        flexShrink: 0,
        background: "var(--sidebar-bg)",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        position: "sticky",
        top: 0,
        overflow: "hidden",
      }}
    >
      {/* Logo Area */}
      <div
        style={{
          padding: "24px 24px",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
          display: "flex",
          alignItems: "center",
          gap: 12
        }}
      >
        <div style={{
          width: 32,
          height: 32,
          background: "var(--accent)",
          borderRadius: 8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontWeight: 700,
          fontFamily: "'IBM Plex Mono', monospace",
        }}>
          C
        </div>
        <div>
          <span style={{ fontSize: 20, fontWeight: 700, color: "white", letterSpacing: "-0.02em" }}>
            CAI
          </span>
          <span style={{ display: "block", fontSize: 11, color: "var(--sidebar-text)", textTransform: "uppercase", letterSpacing: "0.05em", marginTop: 2 }}>
            Compliance
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: "24px 12px", overflowY: "auto" }}>
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = view === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "12px 16px",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
                fontSize: 14,
                fontWeight: active ? 600 : 500,
                fontFamily: "inherit",
                background: active ? "var(--sidebar-hover)" : "transparent",
                color: active ? "var(--sidebar-active-text)" : "var(--sidebar-text)",
                transition: "all 0.2s ease",
                marginBottom: 4,
                position: "relative",
              }}
              onMouseEnter={(e) => {
                if (!active) {
                  e.currentTarget.style.background = "rgba(255,255,255,0.03)";
                  e.currentTarget.style.color = "var(--sidebar-active-text)";
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.color = "var(--sidebar-text)";
                }
              }}
            >
              {active && (
                <span
                  style={{
                    position: "absolute",
                    left: 0,
                    top: "50%",
                    transform: "translateY(-50%)",
                    width: 4,
                    height: 20,
                    background: "var(--sidebar-active-bar)",
                    borderRadius: "0 4px 4px 0",
                  }}
                />
              )}
              <Icon
                size={18}
                style={{
                  color: active ? "var(--sidebar-active-bar)" : "currentColor",
                  flexShrink: 0
                }}
              />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* User Profile Area */}
      <div style={{ padding: "20px", borderTop: "1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: 8, padding: 12, marginBottom: 12 }}>
          <div style={{ fontSize: 12, color: "var(--sidebar-text)", marginBottom: 4 }}>Current Firm</div>
          <div style={{ fontSize: 14, fontWeight: 600, color: "white", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {user?.firm_name || "CA Firm"}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, overflow: "hidden" }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: "50%",
                background: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 14,
                fontWeight: 600,
                color: "white",
                flexShrink: 0,
              }}
            >
              {initial}
            </div>
            <div style={{ overflow: "hidden" }}>
              <div style={{ fontSize: 13, fontWeight: 500, color: "white", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                {user?.name || "User"}
              </div>
              <div style={{ fontSize: 11, color: "var(--sidebar-text)", textTransform: "uppercase" }}>
                {user?.role || "Admin"}
              </div>
            </div>
          </div>

          <button
            onClick={onLogout}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--sidebar-text)",
              cursor: "pointer",
              padding: 8,
              borderRadius: 6,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s"
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = "white"; e.currentTarget.style.background = "rgba(255,255,255,0.1)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = "var(--sidebar-text)"; e.currentTarget.style.background = "transparent"; }}
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}