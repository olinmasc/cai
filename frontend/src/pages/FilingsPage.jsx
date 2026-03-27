import { useState, useEffect, useRef } from "react";
import { Plus, Play, Upload, CheckCircle, AlertCircle } from "lucide-react";
import { api } from "../lib/api.js";
import { useToast } from "../hooks/useToast.jsx";
import { StatusBadge, RiskScore, SkeletonRow } from "../components/ui/UI.jsx";

export default function FilingsPage({ user }) {
  const toast = useToast();
  const [filings, setFilings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState(null);
  const [uploadingId, setUploadingId] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const fileInputRefs = useRef({});

  const isAdmin = user?.role === "Admin";

  const load = async () => {
    setLoading(true);
    const { data } = await api.get("/filings/");
    setFilings(Array.isArray(data) ? data : []);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  // ── UPLOAD XML FOR A CLIENT ──────────────────────────────
  async function handleUpload(f, file) {
    if (!file) return;
    if (!f.client_id) {
      toast("Missing client ID — cannot upload.", "error");
      return;
    }

    setUploadingId(f.id);
    const form = new FormData();
    form.append("file", file);

    const { error } = await api.upload(`/clients/${f.client_id}/upload-file`, form);

    if (error) {
      toast(`Upload failed: ${error}`, "error");
    } else {
      toast(`File uploaded for ${f.client_name}. You can now run the AI pipeline.`, "success");
    }
    setUploadingId(null);
  }

  // ── RUN AI PIPELINE ──────────────────────────────────────
  async function runAI(f) {
    if (!f.client_id) {
      toast("Missing Client ID for this filing.", "error");
      return;
    }

    setRunningId(f.id);
    console.log("Starting AI Pipeline for:", f.client_name, "client_id:", f.client_id);

    const { data, error } = await api.post("/ai/run", {
      client_id: String(f.client_id),
      period: f.period || "03-2026",
    });

    if (error) {
      // Friendly hint if the file hasn't been uploaded yet
      if (error.includes("No source file")) {
        toast(
          `No file uploaded for ${f.client_name}. Use the Upload XML button first.`,
          "error"
        );
      } else {
        toast(error, "error");
      }
    } else {
      toast(
        `AI Pipeline complete for ${f.client_name} — Risk score: ${data?.risk_score ?? "—"}`,
        "success"
      );
      load();
    }

    setRunningId(null);
  }

  return (
    <div style={{ padding: 30 }}>
      {/* ── HEADER ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>Filings</h2>
        {isAdmin && (
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Plus size={16} />
            New Filing
          </button>
        )}
      </div>

      {/* ── TABLE ── */}
      <table className="data-table">
        <thead>
          <tr>
            <th>Client</th>
            <th>Period</th>
            <th>Risk</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <SkeletonRow cols={5} />
          ) : filings.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ textAlign: "center", padding: "40px 0", color: "var(--color-text-secondary)" }}>
                No filings yet. Create one to get started.
              </td>
            </tr>
          ) : (
            filings.map((f) => (
              <tr key={f.id}>
                <td>{f.client_name}</td>
                <td>{f.period}</td>
                <td><RiskScore score={f.risk_score || 0} /></td>
                <td><StatusBadge status={f.status} /></td>
                <td>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>

                    {/* Hidden file input per row */}
                    <input
                      type="file"
                      accept=".xml,.csv"
                      style={{ display: "none" }}
                      ref={(el) => { fileInputRefs.current[f.id] = el; }}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleUpload(f, file);
                        // Reset so same file can be re-uploaded
                        e.target.value = "";
                      }}
                    />

                    {/* Upload XML button */}
                    <button
                      className="btn btn-secondary btn-sm"
                      disabled={uploadingId === f.id}
                      onClick={() => fileInputRefs.current[f.id]?.click()}
                      title="Upload Tally XML or CSV for this client"
                    >
                      <Upload size={14} />
                      {uploadingId === f.id ? "Uploading..." : "Upload XML"}
                    </button>

                    {/* Run AI button */}
                    <button
                      className="btn btn-primary btn-sm"
                      disabled={runningId === f.id || uploadingId === f.id}
                      onClick={() => runAI(f)}
                      title="Run AI reconciliation pipeline"
                    >
                      <Play size={14} />
                      {runningId === f.id ? "Processing..." : "Run AI"}
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}