import { useState, useEffect, useRef } from "react";
import { Plus, Upload, Play, CheckCircle, X, Trash2, FileText } from "lucide-react";
import { api } from "../lib/api.js";
import { useToast } from "../hooks/useToast.jsx";
import {
  RiskScore, StatusBadge, SkeletonRow, EmptyState,
} from "../components/ui/UI.jsx";

// ── ADD CLIENT MODAL ──────────────────────────────────────────
function AddClientModal({ onClose, onAdded }) {
  const toast = useToast();
  const [form, setForm] = useState({
    name: "", gstin: "", phone: "",
  });
  const [saving, setSaving] = useState(false);

  const handleGstinChange = (e) => {
    const val = e.target.value.toUpperCase().slice(0, 15);
    setForm((p) => ({ ...p, gstin: val }));
  };

  const handlePhoneChange = (e) => {
    const val = e.target.value.replace(/\D/g, "").slice(0, 10);
    setForm((p) => ({ ...p, phone: val }));
  };

  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  async function submit() {
    if (!form.name || !form.gstin) {
      toast("Client name and GSTIN are required.", "warning");
      return;
    }
    if (form.gstin.length !== 15) {
      toast("GSTIN must be exactly 15 characters long.", "warning");
      return;
    }
    if (form.phone && form.phone.length !== 10) {
      toast("Phone number must be exactly 10 digits.", "warning");
      return;
    }

    setSaving(true);
    const payload = { ...form };
    if (payload.phone) {
      payload.phone = `+91${payload.phone}`;
    }

    const { data, error } = await api.post("/clients/", payload);
    if (error) {
      toast(error, "error");
    } else {
      toast(`${data.name} added successfully.`, "success");
      onAdded(data);
      onClose();
    }
    setSaving(false);
  }

  return (
    <div
      style={{
        position: "fixed", inset: 0,
        background: "rgba(0,0,0,0.7)",
        backdropFilter: "blur(4px)",
        display: "flex", alignItems: "center",
        justifyContent: "center", zIndex: 50, padding: 16,
      }}
    >
      <div
        className="modal-panel card"
        style={{ width: "100%", maxWidth: 420, boxShadow: "0 24px 48px rgba(0,0,0,0.5)" }}
      >
        <div
          style={{
            display: "flex", alignItems: "center",
            justifyContent: "space-between",
            padding: "18px 20px",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>
            Add Client
          </div>
          <button onClick={onClose} className="btn btn-ghost btn-sm" style={{ padding: "5px 7px" }}>
            <X size={14} />
          </button>
        </div>

        <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label className="label">Client Name</label>
            <input
              className="input"
              value={form.name}
              onChange={set("name")}
            />
          </div>

          <div>
            <label className="label">GSTIN (15 Characters)</label>
            <input
              className="input mono"
              value={form.gstin}
              onChange={handleGstinChange}
            />
          </div>

          <div>
            <label className="label">Phone (10 Digits)</label>
            <div style={{ display: "flex", gap: 8 }}>
              <div style={{
                display: "flex", alignItems: "center", justifyContent: "center",
                background: "var(--bg-lighter)", border: "1px solid var(--border)",
                borderRadius: 6, padding: "0 12px", color: "var(--text-2)", fontSize: 13,
                fontWeight: 500
              }}>
                +91
              </div>
              <input
                className="input mono"
                style={{ flex: 1 }}
                value={form.phone}
                onChange={handlePhoneChange}
              />
            </div>
          </div>
        </div>

        <div
          style={{
            display: "flex", gap: 8,
            padding: "14px 20px",
            borderTop: "1px solid var(--border)",
          }}
        >
          <button onClick={onClose} className="btn btn-secondary" style={{ flex: 1 }}>
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={saving}
            className="btn btn-primary"
            style={{ flex: 1 }}
          >
            {saving ? "Saving..." : "Add Client"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── VALIDATE GST MODAL ────────────────────────────────────────
function GSTResult({ result, onClose }) {
  if (!result) return null;
  return (
    <div
      style={{
        position: "fixed", inset: 0,
        background: "rgba(0,0,0,0.65)",
        backdropFilter: "blur(4px)",
        display: "flex", alignItems: "center",
        justifyContent: "center", zIndex: 50, padding: 16,
      }}
    >
      <div
        className="modal-panel card"
        style={{ width: "100%", maxWidth: 340, padding: 24 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
          {result.is_valid
            ? <CheckCircle size={16} style={{ color: "var(--accent)" }} />
            : <X size={16} style={{ color: "var(--danger)" }} />}
          <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>
            {result.is_valid ? "GSTIN Valid" : "GSTIN Invalid"}
          </span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { label: "GSTIN", value: result.gstin },
            { label: "Legal Name", value: result.legal_name },
            { label: "Status", value: result.status },
          ].map((r) => (
            <div key={r.label} style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: 12, color: "var(--text-3)" }}>{r.label}</span>
              <span
                className="mono"
                style={{ fontSize: 12, color: "var(--text)", fontWeight: 500 }}
              >
                {r.value}
              </span>
            </div>
          ))}
        </div>
        <button
          onClick={onClose}
          className="btn btn-secondary"
          style={{ width: "100%", marginTop: 18 }}
        >
          Close
        </button>
      </div>
    </div>
  );
}

// ── MAIN CLIENTS PAGE ─────────────────────────────────────────
export default function ClientsPage({ user, onRunPipeline }) {
  const toast = useToast();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [uploading, setUploading] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState({});
  const [gstResult, setGstResult] = useState(null);
  const isAdmin = user?.role === "Admin";

  const fileRefs = useRef({});

  const load = async () => {
    setLoading(true);
    const { data } = await api.get("/clients/");
    setClients(Array.isArray(data) ? data : []);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  async function handleFileUpload(e, clientId) {
    const file = e.target.files[0];
    if (!file) return;
    e.target.value = null;

    setUploading(clientId);
    const form = new FormData();
    form.append("file", file);

    const isXML = file.name.toLowerCase().endsWith(".xml");
    const path = isXML
      ? `/clients/${clientId}/upload-xml`
      : `/clients/${clientId}/upload-invoices`;

    const { data, error } = await api.upload(path, form);
    if (error) {
      toast(error, "error");
    } else {
      toast(`Parsed ${data.inserted_count ?? 0} invoices from ${file.name}.`, "success");
      setUploadSuccess(p => ({ ...p, [clientId]: true }));
    }
    setUploading(null);
  }

  async function validateGST(gstin) {
    const { data, error } = await api.post("/clients/validate-gst", { gstin });
    if (error) { toast(error, "error"); return; }
    setGstResult(data);
  }

  async function handleDeleteClient(clientId, clientName) {
    if (!isAdmin) {
      toast("Only Admins can delete clients.", "warning");
      return;
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete "${clientName}"?\n\nThis will permanently delete the client and ALL of their associated invoices, filings, and exceptions.`
    );

    if (!confirmed) return;

    const { error } = await api.delete(`/clients/${clientId}`);
    if (error) {
      toast(error, "error");
    } else {
      toast(`${clientName} deleted successfully.`, "success");
      setClients(clients.filter(c => c.id !== clientId));
    }
  }

  return (
    <div style={{ padding: "28px 32px", maxWidth: 1200 }}>
      <div className="page-header">
        <div>
          <div className="page-title">Clients</div>
          <div className="page-subtitle">
            {loading ? "Loading..." : `${clients.length} client${clients.length !== 1 ? "s" : ""} registered`}
          </div>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="btn btn-primary"
        >
          <Plus size={13} /> Add Client
        </button>
      </div>

      <div className="card" style={{ overflowX: "auto" }}>
        <table className="data-table">
          <thead>
            <tr>
              {["Client", "GSTIN", "Phone", "Risk", "Actions"].map((h) => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <>
                <SkeletonRow cols={5} />
                <SkeletonRow cols={5} />
                <SkeletonRow cols={5} />
              </>
            ) : clients.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: 0 }}>
                  <EmptyState
                    icon={Plus}
                    title="No clients yet"
                    description="Add your first client to get started with invoice reconciliation."
                    action={
                      <button
                        onClick={() => setShowAdd(true)}
                        className="btn btn-primary btn-sm"
                      >
                        <Plus size={12} /> Add Client
                      </button>
                    }
                  />
                </td>
              </tr>
            ) : (
              clients.map((c) => (
                <tr key={c.id}>
                  <td>
                    <div style={{ fontWeight: 500, color: "var(--text)", fontSize: 13 }}>
                      {c.name}
                    </div>
                    <div
                      style={{ fontSize: 11.5, color: "var(--text-3)", marginTop: 2 }}
                    >
                      {c.status || "active"}
                    </div>
                  </td>

                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span className="mono" style={{ color: "var(--text-2)", fontSize: 12 }}>
                        {c.gstin}
                      </span>
                      <button
                        onClick={() => validateGST(c.gstin)}
                        className="btn btn-ghost btn-sm"
                        style={{ fontSize: 10.5, padding: "3px 7px", color: "var(--info)" }}
                      >
                        Verify
                      </button>
                    </div>
                  </td>

                  <td style={{ color: "var(--text-2)", fontSize: 13 }}>
                    {c.phone || <span style={{ color: "var(--text-3)" }}>—</span>}
                  </td>

                  <td>
                    <RiskScore score={c.risk_score || 0} />
                  </td>

                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <input
                        type="file"
                        accept=".xml,.csv,.xlsx"
                        style={{ display: "none" }}
                        ref={(el) => { if (el) fileRefs.current[c.id] = el; }}
                        onChange={(e) => handleFileUpload(e, c.id)}
                      />

                      <button
                        onClick={() => fileRefs.current[c.id]?.click()}
                        disabled={uploading === c.id}
                        className={`btn btn-sm ${uploadSuccess[c.id] ? "btn-accent-outline" : "btn-secondary"}`}
                        style={{ color: uploadSuccess[c.id] ? "var(--accent)" : "var(--info)" }}
                      >
                        {uploadSuccess[c.id] ? <CheckCircle size={11} /> : <Upload size={11} />}
                        {uploading === c.id ? "..." : uploadSuccess[c.id] ? "Uploaded" : "Upload"}
                      </button>

                      <button
                        onClick={() => onRunPipeline(c)}
                        className="btn btn-accent-outline btn-sm"
                      >
                        <Play size={11} /> Run AI
                      </button>

                      {/* ── NEW GENERATE REPORT BUTTON ── */}
                      <GenerateReportButton clientId={c.id} clientName={c.name} />

                      {isAdmin && (
                        <button
                          onClick={() => handleDeleteClient(c.id, c.name)}
                          className="btn btn-ghost btn-sm"
                          style={{ color: "var(--danger)", padding: "6px" }}
                          title="Delete Client"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showAdd && (
        <AddClientModal
          onClose={() => setShowAdd(false)}
          onAdded={(c) => setClients((p) => [...p, c])}
        />
      )}

      {gstResult && (
        <GSTResult result={gstResult} onClose={() => setGstResult(null)} />
      )}
    </div>
  );
}

// ── REPORT GENERATOR COMPONENT ────────────────────────────────
export function GenerateReportButton({ clientId, clientName }) {
  const toast = useToast();
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    // FIXED: Removed .show from the toast calls!
    toast("Drafting audit report...", "info");

    const { blob, error } = await api.download(`/audit/generate-blueprint/${clientId}`);

    if (error) {
      toast(error, "error");
      setIsGenerating(false);
      return;
    }

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Draft_Audit_Report_${clientName.replace(/\s+/g, '_')}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    toast("Report drafted successfully!", "success");
    setIsGenerating(false);
  };

  return (
    <button
      onClick={handleGenerate}
      disabled={isGenerating}
      className="btn btn-secondary btn-sm"
      style={{ color: "var(--accent)", display: "flex", alignItems: "center", gap: 6 }}
    >
      <FileText size={11} />
      {isGenerating ? "..." : "Draft"}
    </button>
  );
}