import { useState, useEffect, useRef } from "react";
import {
  RefreshCw, FileText, Shield, Zap, Brain, CheckCircle,
} from "lucide-react";
import { api } from "../lib/api.js";
import { useToast } from "../hooks/useToast.jsx";

const AGENT_ICONS = {
  Ingestion:      FileText,
  Reconciliation: Shield,
  Filing:         Zap,
  Learning:       Brain,
};

const AGENT_COLORS = {
  Ingestion:      "var(--accent)",
  Reconciliation: "#a78bfa",
  Filing:         "var(--warning)",
  Learning:       "var(--info)",
};

const DEMO_LOGS = [
  { agent: "Ingestion",      level: "info",    text: "Reading uploaded data for Sharma Traders..." },
  { agent: "Ingestion",      level: "info",    text: "Extracted 142 invoices from file" },
  { agent: "Ingestion",      level: "success", text: "Ingestion complete — 0 parse errors" },
  { agent: "Reconciliation", level: "info",    text: "Fetching GSTR-2A data (Mar 2026)..." },
  { agent: "Reconciliation", level: "warning", text: "Mismatch: Invoice #SH-2291 — amount differs by ₹1,240" },
  { agent: "Reconciliation", level: "warning", text: "GSTIN not found in GSTR-2A: 27BBBCR5678D1ZQ" },
  { agent: "Reconciliation", level: "success", text: "141/142 invoices matched — risk score: 12" },
  { agent: "Filing",         level: "info",    text: "Auto-filling GSTR-3B payload..." },
  { agent: "Filing",         level: "info",    text: "Payload validated — ₹4,28,750 taxable supply" },
  { agent: "Filing",         level: "success", text: "GSTR-3B filed — Ref: NIC20260312001432" },
  { agent: "Learning",       level: "info",    text: "Updating anomaly model with new patterns..." },
  { agent: "Learning",       level: "success", text: "Model retrained — F1: 0.9420 (+0.011)" },
];

const LOG_COLORS = {
  info:    "var(--text-2)",
  success: "var(--accent)",
  warning: "var(--warning)",
  error:   "var(--danger)",
};

export default function AgentStatusPage() {
  const toast = useToast();
  const [status, setStatus]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs]       = useState([]);
  const [running, setRunning] = useState(false);
  const logsRef               = useRef(null);

  const loadStatus = async () => {
    setLoading(true);
    const { data, error } = await api.get("/ai/status");
    if (error) {
      toast(error, "error");
    } else {
      setStatus(data);
    }
    setLoading(false);
  };

  useEffect(() => { loadStatus(); }, []);

  useEffect(() => {
    logsRef.current?.scrollTo({ top: 9999, behavior: "smooth" });
  }, [logs]);

  function simulateRun() {
    setLogs([]);
    setRunning(true);
    let i = 0;
    const interval = setInterval(() => {
      if (i >= DEMO_LOGS.length) {
        clearInterval(interval);
        setRunning(false);
        return;
      }
      const entry = {
        ...DEMO_LOGS[i],
        id:   Date.now() + i,
        time: new Date().toLocaleTimeString(),
      };
      setLogs((p) => [...p, entry]);
      i++;
    }, 450);
  }

  return (
    <div style={{ padding: "28px 32px", maxWidth: 900 }}>
      <div className="page-header">
        <div>
          <div className="page-title">Agent Status</div>
          <div className="page-subtitle">
            LangGraph pipeline &mdash; 4-agent orchestration
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={loadStatus}
            disabled={loading}
            className="btn btn-secondary btn-sm"
          >
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
            Refresh Status
          </button>
          <button
            onClick={simulateRun}
            disabled={running}
            className="btn btn-accent-outline btn-sm"
          >
            <RefreshCw size={12} className={running ? "animate-spin" : ""} />
            {running ? "Running..." : "Simulate Run"}
          </button>
        </div>
      </div>

      {/* Agent cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
        {(status?.agents || [
          { name: "Ingestion",      status: "ready", sub: "Perceive" },
          { name: "Reconciliation", status: "ready", sub: "Reason"  },
          { name: "Filing",         status: "ready", sub: "Act"     },
          { name: "Learning",       status: "ready", sub: "Reflect" },
        ]).map((agent) => {
          const Icon  = AGENT_ICONS[agent.name] || FileText;
          const color = AGENT_COLORS[agent.name] || "var(--accent)";
          const isReady = agent.status === "ready";
          return (
            <div
              key={agent.name}
              className="card"
              style={{
                padding: 18,
                borderColor: isReady ? `${color}30` : "var(--border)",
              }}
            >
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 8,
                  background: `${color}12`,
                  border: `1px solid ${color}25`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: 14,
                }}
              >
                <Icon size={16} style={{ color }} />
              </div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)", marginBottom: 4 }}>
                {agent.name}
              </div>
              <div style={{ fontSize: 11.5, color: "var(--text-3)", marginBottom: 10 }}>
                {agent.sub}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                {isReady
                  ? <CheckCircle size={12} style={{ color: "var(--accent)" }} />
                  : (
                    <span
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        background: "var(--warning)",
                        display: "block",
                      }}
                    />
                  )}
                <span
                  style={{
                    fontSize: 11.5,
                    fontWeight: 500,
                    color: isReady ? "var(--accent)" : "var(--warning)",
                    textTransform: "capitalize",
                  }}
                >
                  {agent.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Model info */}
      {status && (
        <div
          className="card"
          style={{ padding: "14px 18px", marginBottom: 20, display: "flex", alignItems: "center", gap: 20 }}
        >
          <div>
            <div style={{ fontSize: 11.5, color: "var(--text-3)", marginBottom: 3 }}>
              ML Model
            </div>
            <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
              XGBoost Anomaly Detector
            </div>
          </div>
          <div
            style={{
              width: 1,
              height: 28,
              background: "var(--border)",
            }}
          />
          <div>
            <div style={{ fontSize: 11.5, color: "var(--text-3)", marginBottom: 3 }}>
              Trained
            </div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 500,
                color: status.model_trained ? "var(--accent)" : "var(--warning)",
              }}
            >
              {status.model_trained ? "Yes" : "Pending"}
            </div>
          </div>
          <div
            style={{ width: 1, height: 28, background: "var(--border)" }}
          />
          <div>
            <div style={{ fontSize: 11.5, color: "var(--text-3)", marginBottom: 3 }}>
              MLflow Tracking
            </div>
            <span
              className="mono"
              style={{ fontSize: 12, color: "var(--text-2)" }}
            >
              {status.mlflow_tracking}
            </span>
          </div>
          <div
            style={{ width: 1, height: 28, background: "var(--border)" }}
          />
          <div>
            <div style={{ fontSize: 11.5, color: "var(--text-3)", marginBottom: 3 }}>
              Version
            </div>
            <span
              className="mono"
              style={{ fontSize: 12, color: "var(--text-2)" }}
            >
              {status.version}
            </span>
          </div>
        </div>
      )}

      {/* Log terminal */}
      <div>
        <div className="section-label">Agent Log</div>
        <div
          className="card"
          style={{ overflow: "hidden" }}
        >
          {/* Terminal chrome */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "10px 16px",
              borderBottom: "1px solid var(--border)",
              background: "var(--surface-2)",
            }}
          >
            <div style={{ display: "flex", gap: 6 }}>
              {["#ef4444", "#f59e0b", "#10b981"].map((c, i) => (
                <div
                  key={i}
                  style={{ width: 10, height: 10, borderRadius: "50%", background: c, opacity: 0.7 }}
                />
              ))}
            </div>
            <span
              className="mono"
              style={{ fontSize: 11, color: "var(--text-3)" }}
            >
              cai-agent-log
            </span>
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: "50%",
                  background: running ? "var(--accent)" : "var(--text-3)",
                  display: "block",
                  animation: running ? "pulse 1.2s infinite" : "none",
                }}
              />
              <span style={{ fontSize: 11, color: "var(--text-3)" }}>
                {running ? "live" : "idle"}
              </span>
            </div>
          </div>

          {/* Log content */}
          <div
            ref={logsRef}
            style={{
              padding: "14px 16px",
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 12,
              minHeight: 220,
              maxHeight: 320,
              overflowY: "auto",
              background: "var(--bg)",
              display: "flex",
              flexDirection: "column",
              gap: 5,
            }}
          >
            {logs.length === 0 ? (
              <span style={{ color: "var(--text-3)" }}>
                Press "Simulate Run" to watch the agents process invoices in real-time...
              </span>
            ) : (
              logs.map((log) => (
                <div key={log.id} style={{ display: "flex", gap: 14 }}>
                  <span style={{ color: "var(--text-3)", flexShrink: 0, fontSize: 11 }}>
                    {log.time}
                  </span>
                  <span
                    style={{
                      color: AGENT_COLORS[log.agent] || "var(--text-3)",
                      flexShrink: 0,
                      fontSize: 11,
                    }}
                  >
                    [{log.agent}]
                  </span>
                  <span style={{ color: LOG_COLORS[log.level] || "var(--text-2)" }}>
                    {log.text}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
