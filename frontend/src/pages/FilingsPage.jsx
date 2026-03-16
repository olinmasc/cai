import { useState, useEffect } from "react";
import { FileText, Plus, Check, AlertCircle, RefreshCw, X } from "lucide-react";
import { api } from "../lib/api.js";
import { useToast } from "../hooks/useToast.jsx";
import { StatusBadge, RiskScore, SkeletonRow, EmptyState } from "../components/ui/UI.jsx";

// ── CREATE FILING MODAL ───────────────────────────────────────
function CreateFilingModal({ onClose, onCreated }) {
  const toast = useToast();
  const [clients, setClients] = useState([]);
  const [form, setForm] = useState({ client_id: "", period: "03-2026", return_type: "GSTR-3B" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/clients/").then(({ data }) => {
      if (Array.isArray(data)) {
        setClients(data);
        if (data.length > 0) setForm((p) => ({ ...p, client_id: data[0].id }));
      }
    });
  }, []);

  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  async function submit() {
    if (!form.client_id) { toast("Select a client.", "warning"); return; }
    setSaving(true);
    const { data, error } = await api.post("/filings/", form);
    if (error) {
      toast(error, "error");
    } else {
      toast("Filing created successfully.", "success");
      onCreated(data);
      onClose();
    }
    setSaving(false);
  }

  const PERIODS = ["01-2026", "02-2026", "03-2026", "10-2025", "11-2025", "12-2025"];

  return (
    <div
      style={{
        position: "fixed", inset: 0,
        background: "rgba(17, 24, 39, 0.4)", backdropFilter: "blur(4px)",
        display: "flex", alignItems: "center",
        justifyContent: "center", zIndex: 50, padding: 16,
      }}
    >
      <div className="card" style={{ width: "100%", maxWidth: 440, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 24px", borderBottom: "1px solid var(--border)", background: "var(--surface-2)", borderRadius: "10px 10px 0 0" }}>
          <div style={{ fontSize: 15, fontWeight: 600, color: "var(--text)" }}>Schedule New Filing</div>
          <button onClick={onClose} className="btn btn-ghost btn-sm" style={{ padding: 6 }}><X size={16} /></button>
        </div>

        <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label className="label">Target Client</label>
            <select className="input" value={form.client_id} onChange={set("client_id")} style={{ cursor: "pointer" }}>
              {clients.length === 0 && <option value="">Loading portfolio...</option>}
              {clients.map((c) => <option key={c.id} value={c.id}>{c.name} — {c.gstin}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Filing Period</label>
            <select className="input" value={form.period} onChange={set("period")} style={{ cursor: "pointer" }}>
              {PERIODS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <label className="label">GST Return Type</label>
            <select className="input" value={form.return_type} onChange={set("return_type")} style={{ cursor: "pointer" }}>
              <option value="GSTR-3B">GSTR-3B (Summary Return)</option>
              <option value="GSTR-1">GSTR-1 (Outward Supplies)</option>
              <option value="GSTR-9">GSTR-9 (Annual Return)</option>
            </select>
          </div>
        </div>

        <div style={{ display: "flex", gap: 12, padding: "16px 24px", borderTop: "1px solid var(--border)", background: "var(--surface-2)", borderRadius: "0 0 10px 10px" }}>
          <button onClick={onClose} className="btn btn-secondary" style={{ flex: 1 }}>Cancel</button>
          <button onClick={submit} disabled={saving} className="btn btn-primary" style={{ flex: 1 }}>
            {saving ? "Scheduling..." : "Create Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── MAIN FILINGS PAGE ─────────────────────────────────────────
export default function FilingsPage({ user }) {
  const toast = useToast();
  const [filings, setFilings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [actioning, setActioning] = useState(null);
  const isAdmin = user?.role === "Admin";

  const load = async () => {
    setLoading(true);
    const { data } = await api.get("/filings/");
    setFilings(Array.isArray(data) ? data : []);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  async function markFiled(id) {
    if (!isAdmin) { toast("Only Admins can finalize filings.", "warning"); return; }
    setActioning(id);
    const { error } = await api.put(`/filings/${id}/file`);
    if (error) {
      toast(error, "error");
    } else {
      setFilings((p) => p.map((f) => f.id === id ? { ...f, status: "filed", filed_at: new Date().toISOString() } : f));
      toast("Filing marked as complete.", "success");
    }
    setActioning(null);
  }

  async function markError(id) {
    if (!isAdmin) { toast("Only Admins can flag errors.", "warning"); return; }
    setActioning(id);
    const { error } = await api.put(`/filings/${id}/error`);
    if (error) {
      toast(error, "error");
    } else {
      setFilings((p) => p.map((f) => f.id === id ? { ...f, status: "error" } : f));
      toast("Filing flagged for review.", "warning");
    }
    setActioning(null);
  }

  const pending = filings.filter((f) => f.status === "pending").length;
  const filed = filings.filter((f) => f.status === "filed").length;
  const errors = filings.filter((f) => f.status === "error").length;

  return (
    <div style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <div className="page-header" style={{ marginBottom: 32 }}>
        <div>
          <div className="page-title">Filing Submissions</div>
          <div className="page-subtitle">
            {loading ? "Syncing data..." : `Tracking ${filings.length} total filings`}
          </div>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <button onClick={load} disabled={loading} className="btn btn-secondary">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refresh
          </button>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Plus size={16} /> New Filing
          </button>
        </div>
      </div>

      {!loading && filings.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginBottom: 24 }}>
          {[
            { label: "Pending Submission", value: pending, color: "var(--warning)", bg: "var(--warning-dim)" },
            { label: "Successfully Filed", value: filed, color: "var(--success)", bg: "rgba(16,185,129,0.1)" },
            { label: "Processing Errors", value: errors, color: "var(--danger)", bg: "var(--danger-dim)" },
          ].map((s) => (
            <div key={s.label} className="card" style={{ padding: "20px 24px", display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: s.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <FileText size={24} style={{ color: s.color }} />
              </div>
              <div>
                <div className="mono" style={{ fontSize: 24, fontWeight: 600, color: "var(--text)", lineHeight: 1.2 }}>{s.value}</div>
                <div style={{ fontSize: 13, color: "var(--text-3)", fontWeight: 500 }}>{s.label}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="card" style={{ overflow: "hidden" }}>
        <table className="data-table">
          <thead>
            <tr>
              {["Client / Entity", "Tax Period", "Form Type", "Calculated Risk", "Status", "Completion Date", "Management"].map((h) => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <>
                <SkeletonRow cols={7} />
                <SkeletonRow cols={7} />
                <SkeletonRow cols={7} />
              </>
            ) : filings.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: 0 }}>
                  <EmptyState icon={FileText} title="No filing history" description="Run the AI compliance pipeline on a client to automatically generate drafts." action={<button onClick={() => setShowCreate(true)} className="btn btn-primary"><Plus size={14} /> Draft Manual Filing</button>} />
                </td>
              </tr>
            ) : (
              filings.map((f) => (
                <tr key={f.id} style={{ opacity: f.status === "error" ? 0.7 : 1 }}>
                  <td><div style={{ fontWeight: 600, color: "var(--text)", fontSize: 13.5 }}>{f.client_name || f.client_id?.slice(-6)}</div></td>
                  <td><span className="mono" style={{ fontSize: 13, color: "var(--text-2)", fontWeight: 500 }}>{f.period}</span></td>
                  <td>
                    <span className="mono" style={{ fontSize: 12, color: "var(--accent)", background: "var(--accent-dim)", padding: "4px 8px", borderRadius: 6, fontWeight: 600 }}>
                      {f.return_type}
                    </span>
                  </td>
                  <td><RiskScore score={f.risk_score || 0} /></td>
                  <td><StatusBadge status={f.status} /></td>
                  <td>
                    <span style={{ fontSize: 13, color: "var(--text-2)" }}>
                      {f.filed_at ? new Date(f.filed_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "—"}
                    </span>
                  </td>
                  <td>
                    {f.status === "pending" && isAdmin && (
                      <div style={{ display: "flex", gap: 8 }}>
                        <button onClick={() => markFiled(f.id)} disabled={actioning === f.id} className="btn btn-secondary btn-sm" style={{ color: "var(--success)" }}>
                          <Check size={14} /> {actioning === f.id ? "..." : "Confirm"}
                        </button>
                        <button onClick={() => markError(f.id)} disabled={actioning === f.id} className="btn btn-ghost btn-sm" style={{ color: "var(--danger)" }}>
                          <AlertCircle size={14} /> Flag
                        </button>
                      </div>
                    )}
                    {f.status === "filed" && <span className="mono" style={{ fontSize: 12, color: "var(--text-3)" }}>{f.nic_reference || "VERIFIED"}</span>}
                    {f.status === "error" && <span style={{ fontSize: 12, color: "var(--danger)", fontWeight: 500 }}>Requires Review</span>}
                    {!isAdmin && f.status === "pending" && <span style={{ fontSize: 12, color: "var(--text-3)" }}>Admin Access Required</span>}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {showCreate && <CreateFilingModal onClose={() => setShowCreate(false)} onCreated={(f) => { setFilings((p) => [f, ...p]); }} />}
    </div>
  );
}