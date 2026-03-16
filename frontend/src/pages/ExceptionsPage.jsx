import { useState, useEffect } from "react";
import { AlertTriangle, MessageSquare, Check, X, RefreshCw } from "lucide-react";
import { api } from "../lib/api.js";
import { useToast } from "../hooks/useToast.jsx";
import { RiskScore, StatusBadge, SkeletonRow, EmptyState } from "../components/ui/UI.jsx";

export default function ExceptionsPage({ user }) {
  const toast = useToast();
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actioning, setActioning] = useState(null);
  const isAdmin = user?.role === "Admin";

  const load = async () => {
    setLoading(true);
    const { data: clients } = await api.get("/clients/");
    if (!Array.isArray(clients)) { setLoading(false); return; }

    const results = await Promise.all(
      clients.map(async (c) => {
        const { data: exs } = await api.get(`/reconciliation/${c.id}`);
        return Array.isArray(exs) ? exs.map((e) => ({ ...e, client_name: c.name, client_phone: c.phone })) : [];
      })
    );

    setExceptions(results.flat());
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  async function approve(id) {
    if (!isAdmin) { toast("Only Admins can override exceptions.", "warning"); return; }
    setActioning(id);
    const { data, error } = await api.post(`/reconciliation/approve/${id}`, {});
    if (error) { toast(error, "error"); }
    else {
      setExceptions((p) => p.map((e) => (e.id === id ? { ...e, status: "approved" } : e)));
      toast("Exception verified and audit logged.", "success");
    }
    setActioning(null);
  }

  function dismiss(id) {
    setExceptions((p) => p.map((e) => (e.id === id ? { ...e, status: "dismissed" } : e)));
    toast("Exception cleared from queue.", "info");
  }

  async function notifyClient(ex) {
    if (!isAdmin) { toast("Only Admins can trigger client alerts.", "warning"); return; }
    setActioning(`notify-${ex.id}`);
    const { data, error } = await api.post("/reconciliation/notify-client", {
      client_id: ex.client_id,
      invoice_no: ex.invoice_id || ex.invoice || "N/A",
      amount: ex.amount || 0,
    });
    if (error) { toast(error, "error"); }
    else { toast(`WhatsApp alert sent to ${ex.client_name}.`, "success"); }
    setActioning(null);
  }

  const pending = exceptions.filter((e) => e.status === "mismatch" || e.status === "pending");

  return (
    <div style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <div className="page-header" style={{ marginBottom: 24 }}>
        <div>
          <div className="page-title">Anomaly Resolution Queue</div>
          <div className="page-subtitle">
            {loading ? "Analyzing ledger..." : `${pending.length} anomalies awaiting review`}
          </div>
        </div>
        <button onClick={load} disabled={loading} className="btn btn-secondary">
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refresh Data
        </button>
      </div>

      {pending.length > 0 && (
        <div style={{ background: "var(--warning-dim)", border: "1px solid rgba(245,158,11,0.3)", borderRadius: 8, padding: "16px 20px", display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
          <div style={{ width: 40, height: 40, borderRadius: 8, background: "rgba(245,158,11,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <AlertTriangle size={20} style={{ color: "var(--warning)" }} />
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>Attention Required</div>
            <div style={{ fontSize: 13, color: "var(--text-2)", marginTop: 2 }}>You have {pending.length} unresolved AI-flagged anomalies that may delay GSTR filings.</div>
          </div>
        </div>
      )}

      <div className="card" style={{ overflow: "hidden" }}>
        <table className="data-table">
          <thead>
            <tr>
              {["Target Entity", "Transaction Ref", "AI Analysis & Reasoning", "Risk Score", "State", "Resolution"].map((h) => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <>
                <SkeletonRow cols={6} />
                <SkeletonRow cols={6} />
                <SkeletonRow cols={6} />
              </>
            ) : exceptions.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: 0 }}>
                  <EmptyState icon={AlertTriangle} title="Clean Ledger" description="No anomalies detected across the current client portfolio." />
                </td>
              </tr>
            ) : (
              exceptions.map((ex) => {
                const isPending = ex.status === "mismatch" || ex.status === "pending";
                return (
                  <tr key={ex.id} style={{ opacity: isPending ? 1 : 0.6, background: isPending ? "transparent" : "var(--surface-2)" }}>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--text)", fontSize: 13.5 }}>{ex.client_name || ex.client_id?.slice(-6)}</div>
                      {ex.client_phone && <div className="mono" style={{ fontSize: 12, color: "var(--text-3)", marginTop: 4 }}>{ex.client_phone}</div>}
                    </td>

                    <td>
                      <span className="mono" style={{ fontSize: 13, color: "var(--text)", fontWeight: 500 }}>{ex.invoice_id || ex.invoice || "—"}</span>
                      {ex.amount != null && <div className="mono" style={{ fontSize: 13, color: "var(--text-2)", marginTop: 4 }}>₹{Number(ex.amount).toLocaleString("en-IN")}</div>}
                    </td>

                    <td style={{ maxWidth: 300 }}>
                      <div style={{ fontSize: 13, color: "var(--text-2)", lineHeight: 1.5 }}>
                        {ex.mismatch_reason || ex.detail || "General data mismatch."}
                      </div>
                      {ex.carried_forward && (
                        <div style={{ display: "inline-block", marginTop: 8, fontSize: 11, fontWeight: 600, color: "var(--warning)", background: "var(--warning-dim)", padding: "2px 8px", borderRadius: 4 }}>
                          Persistent from prior period
                        </div>
                      )}
                    </td>

                    <td><RiskScore score={ex.risk ?? ex.anomaly_score ?? 50} /></td>
                    <td><StatusBadge status={ex.status} /></td>

                    <td>
                      {isPending ? (
                        <div style={{ display: "flex", gap: 8 }}>
                          <button onClick={() => approve(ex.id)} disabled={!isAdmin || actioning === ex.id} className="btn btn-secondary btn-sm" title="Override AI & Approve">
                            <Check size={14} style={{ color: "var(--success)" }} />
                          </button>
                          <button onClick={() => dismiss(ex.id)} disabled={!isAdmin} className="btn btn-secondary btn-sm" title="Dismiss from Queue">
                            <X size={14} style={{ color: "var(--text-3)" }} />
                          </button>
                          <button onClick={() => notifyClient(ex)} disabled={!isAdmin || actioning === `notify-${ex.id}`} className="btn btn-secondary btn-sm" title="Request Clarification via WhatsApp">
                            <MessageSquare size={14} style={{ color: "var(--info)" }} />
                          </button>
                        </div>
                      ) : (
                        <span style={{ fontSize: 12, color: "var(--text-3)", fontWeight: 500 }}>Resolved</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}