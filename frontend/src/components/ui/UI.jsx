// ── STATUS DOT ────────────────────────────────────────────────
export function StatusDot({ status }) {
  return (
    <span
      className="status-dot"
      title={status}
      style={{
        background: resolveStatusColor(status),
      }}
    />
  );
}

function resolveStatusColor(status) {
  const s = (status || "").toLowerCase();
  if (["active", "filed", "matched", "approved", "success"].includes(s)) return "var(--accent)";
  if (["pending", "processing"].includes(s)) return "var(--warning)";
  if (["error", "mismatch", "failed"].includes(s)) return "var(--danger)";
  return "var(--text-3)";
}

// ── RISK SCORE ────────────────────────────────────────────────
export function RiskScore({ score }) {
  const n = Number(score) || 0;
  let color = "var(--accent)";
  if (n > 70) color = "var(--danger)";
  else if (n > 30) color = "var(--warning)";

  return (
    <span
      className="mono"
      style={{ color, fontWeight: 600, fontSize: 13 }}
    >
      {n}
    </span>
  );
}

// ── STATUS BADGE ──────────────────────────────────────────────
export function StatusBadge({ status }) {
  const s = (status || "idle").toLowerCase();
  let cls = "badge-gray";
  let label = status || "idle";

  if (["active", "filed", "matched", "approved", "success", "ready"].includes(s)) {
    cls = "badge-green";
  } else if (["pending", "processing"].includes(s)) {
    cls = "badge-yellow";
  } else if (["error", "mismatch", "failed"].includes(s)) {
    cls = "badge-red";
  } else if (["pilot"].includes(s)) {
    cls = "badge-blue";
  }

  return (
    <span className={`badge ${cls}`} style={{ textTransform: "capitalize" }}>
      {label}
    </span>
  );
}

// ── PLAN BADGE ────────────────────────────────────────────────
export function PlanBadge({ plan }) {
  const p = (plan || "").toLowerCase();
  const map = {
    pilot:     { cls: "badge-blue",   label: "Pilot"     },
    automator: { cls: "badge-green",  label: "Automator" },
    scale:     { cls: "badge-yellow", label: "Scale"     },
  };
  const { cls, label } = map[p] || { cls: "badge-gray", label: plan };
  return <span className={`badge ${cls}`}>{label}</span>;
}

// ── SKELETON ──────────────────────────────────────────────────
export function Skeleton({ w = "100%", h = 16, rounded = 4 }) {
  return (
    <div
      className="skeleton"
      style={{ width: w, height: h, borderRadius: rounded }}
    />
  );
}

export function SkeletonRow({ cols = 5 }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} style={{ padding: "14px 16px", borderBottom: "1px solid var(--border)" }}>
          <Skeleton h={13} w={i === 0 ? 120 : i === cols - 1 ? 80 : 90} />
        </td>
      ))}
    </tr>
  );
}

// ── EMPTY STATE ───────────────────────────────────────────────
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "56px 24px",
        gap: 12,
        textAlign: "center",
      }}
    >
      {Icon && (
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 8,
            background: "var(--surface-3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: 4,
          }}
        >
          <Icon size={18} style={{ color: "var(--text-3)" }} />
        </div>
      )}
      <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text-2)" }}>{title}</div>
      {description && (
        <div style={{ fontSize: 12.5, color: "var(--text-3)", maxWidth: 320, lineHeight: 1.6 }}>
          {description}
        </div>
      )}
      {action && <div style={{ marginTop: 8 }}>{action}</div>}
    </div>
  );
}

// ── DIVIDER ───────────────────────────────────────────────────
export function Divider() {
  return (
    <div style={{ borderTop: "1px solid var(--border)", margin: "20px 0" }} />
  );
}
